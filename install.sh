#!/bin/bash
# install.sh — TOP WorX ERP — نصب کامل روی Ubuntu
set -euo pipefail

# ── رنگ‌ها ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; }
print_header()  {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

generate_password() { openssl rand -base64 32 | tr -d "=+/" | cut -c1-25; }
generate_secret()   { openssl rand -hex 32; }


# ── تنظیم DNS برای Docker daemon ─────────────────────────────────────────────
# Docker build containers inherit DNS from the daemon, not from the host's
# /etc/resolv.conf. On many VPS providers the default resolver is unreachable
# inside containers, causing EAI_AGAIN when npm/pip try to reach the internet.
configure_docker_dns() {
    print_message "تنظیم DNS برای Docker daemon (رفع خطای EAI_AGAIN)..."
    sudo mkdir -p /etc/docker
    if [ -f /etc/docker/daemon.json ]; then
        sudo python3 -c "
import json
with open('/etc/docker/daemon.json') as f:
    cfg = json.load(f)
cfg['dns'] = ['8.8.8.8', '8.8.4.4', '1.1.1.1']
with open('/etc/docker/daemon.json', 'w') as f:
    json.dump(cfg, f, indent=2)
"
    else
        echo '{"dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]}' | sudo tee /etc/docker/daemon.json > /dev/null
    fi
    sudo systemctl restart docker
    sleep 3
    print_message "Docker daemon با DNS ثابت راه‌اندازی مجدد شد"
}
# ── بررسی سیستم‌عامل ─────────────────────────────────────────────────────────
print_header "نصب کامل TOP WorX ERP System"

if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    print_error "این اسکریپت فقط برای Ubuntu طراحی شده است"
    exit 1
fi

# ── دریافت دامنه / IP ────────────────────────────────────────────────────────
read -rp "نام دامنه یا IP سرور را وارد کنید (مثال: example.com): " DOMAIN
[ -z "$DOMAIN" ] && DOMAIN="localhost" && print_warning "دامنه تنظیم نشد. استفاده از localhost"

# ── مرحله 1: پیش‌نیازها ──────────────────────────────────────────────────────
print_header "مرحله 1: نصب پیش‌نیازها"
sudo apt-get update -qq && sudo apt-get upgrade -y -qq

if ! command -v docker &>/dev/null; then
    print_message "نصب Docker..."
    sudo apt-get install -y -qq ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker "$USER"
    print_warning "Docker نصب شد. ممکن است برای اجرای docker بدون sudo نیاز به logout/login داشته باشید"
fi

# تنظیم DNS — باید بعد از نصب Docker اجرا شود
configure_docker_dns

sudo apt-get install -y -qq git openssl

# ── مرحله 2: ساختار پوشه‌ها ──────────────────────────────────────────────────
print_header "مرحله 2: ایجاد ساختار پروژه"
mkdir -p backup logs media static nginx/conf.d postgres/init prometheus grafana/provisioning

# ── مرحله 3: متغیرهای محیطی ──────────────────────────────────────────────────
print_header "مرحله 3: تنظیم متغیرهای محیطی"

POSTGRES_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
SECRET_KEY=$(generate_secret)
GRAFANA_PASSWORD=$(generate_password)
FLOWER_PASSWORD=$(generate_password)

# Note: heredoc uses ENV_EOF (no quotes) so variables expand at write time
cat > .env << ENV_EOF
# TOP WorX ERP — Environment Variables
# تولید شده توسط install.sh — مقادیر را در محیط تولید تغییر دهید

# ── PostgreSQL ────────────────────────────────────────────────────────────────
POSTGRES_DB=topworx_db
POSTGRES_USER=topworx
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_URL=postgresql://topworx:${POSTGRES_PASSWORD}@postgres:5432/topworx_db
SQLALCHEMY_DATABASE_URI=postgresql://topworx:${POSTGRES_PASSWORD}@postgres:5432/topworx_db

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/1

# ── Security ──────────────────────────────────────────────────────────────────
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── Application ───────────────────────────────────────────────────────────────
ENVIRONMENT=production
CORS_ORIGINS=["http://${DOMAIN}","https://${DOMAIN}"]
BACKEND_CORS_ORIGINS=["http://${DOMAIN}","https://${DOMAIN}"]
REACT_APP_API_URL=http://${DOMAIN}/api
REACT_APP_ENVIRONMENT=production
MAX_UPLOAD_SIZE=52428800
ALLOWED_EXTENSIONS=.pdf,.docx,.xlsx,.png,.jpg,.jpeg
UPLOAD_DIR=uploads

# ── Email ─────────────────────────────────────────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@topworx.com
EMAILS_FROM_NAME=TOP WorX

# ── Monitoring ────────────────────────────────────────────────────────────────
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

# ── Flower ────────────────────────────────────────────────────────────────────
FLOWER_USER=admin
FLOWER_PASSWORD=${FLOWER_PASSWORD}

# ── Domain ────────────────────────────────────────────────────────────────────
DOMAIN=${DOMAIN}
ENV_EOF

print_message "فایل .env ایجاد شد"

# ── مرحله 4: docker-compose.yml ──────────────────────────────────────────────
print_header "مرحله 4: ایجاد Docker Compose"

# IMPORTANT: heredoc delimiter is QUOTED ('COMPOSE_EOF') so the dollar signs
# inside are written literally and Docker Compose resolves them from .env at
# runtime. Without quotes the shell would expand them now (to empty strings)
# because POSTGRES_PASSWORD etc. are not exported into this heredoc scope.
cat > docker-compose.yml << 'COMPOSE_EOF'
# docker-compose.yml — TOP WorX ERP
# Auto-loads docker-compose.override.yml when present.
# Production: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

services:

  # ── Database ────────────────────────────────────────────────────────────────
  postgres:
    image: postgres:15-alpine
    container_name: topworx_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-topworx_db}
      POSTGRES_USER: ${POSTGRES_USER:-topworx}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d:ro
    ports:
      - "127.0.0.1:5432:5432"
    networks:
      - topworx_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-topworx} -d ${POSTGRES_DB:-topworx_db}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  # ── Cache / Message broker ──────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: topworx_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - topworx_network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Backend API ─────────────────────────────────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: topworx_backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM:-HS256}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-30}
      - REFRESH_TOKEN_EXPIRE_DAYS=${REFRESH_TOKEN_EXPIRE_DAYS:-7}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - MAX_UPLOAD_SIZE=${MAX_UPLOAD_SIZE:-52428800}
      - ALLOWED_EXTENSIONS=${ALLOWED_EXTENSIONS:-.pdf,.docx,.xlsx,.png,.jpg,.jpeg}
      - UPLOAD_DIR=${UPLOAD_DIR:-uploads}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SMTP_TLS=${SMTP_TLS:-true}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL:-noreply@topworx.com}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    volumes:
      - backend_logs:/app/logs
      - media_files:/app/media
      - backend_uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - topworx_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  # ── Celery Worker ───────────────────────────────────────────────────────────
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: topworx_celery
    restart: unless-stopped
    command: celery -A app.worker worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT:-587}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    volumes:
      - backend_uploads:/app/uploads
      - celery_logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - topworx_network
    healthcheck:
      test: ["CMD-SHELL", "celery -A app.worker inspect ping -d celery@$$HOSTNAME || exit 1"]
      interval: 30s
      timeout: 15s
      retries: 3
      start_period: 20s

  # ── Flower (Celery monitor) ─────────────────────────────────────────────────
  flower:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: topworx_flower
    restart: unless-stopped
    command: >
      celery -A app.worker flower
      --port=5555
      --broker=${CELERY_BROKER_URL}
      --basic_auth=${FLOWER_USER:-admin}:${FLOWER_PASSWORD}
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
      - FLOWER_USER=${FLOWER_USER:-admin}
      - FLOWER_PASSWORD=${FLOWER_PASSWORD}
    ports:
      - "127.0.0.1:5555:5555"
    depends_on:
      - celery
      - redis
    networks:
      - topworx_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5555"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ── Frontend ────────────────────────────────────────────────────────────────
  frontend:
    build:
      context: ./topworx-new
      dockerfile: Dockerfile
    container_name: topworx_frontend
    restart: unless-stopped
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL}
      - REACT_APP_ENVIRONMENT=${REACT_APP_ENVIRONMENT:-production}
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - topworx_network

  # ── Nginx reverse proxy ─────────────────────────────────────────────────────
  nginx:
    image: nginx:alpine
    container_name: topworx_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - media_files:/var/www/media:ro
    depends_on:
      - backend
      - frontend
    networks:
      - topworx_network

# Every named volume used by any service MUST appear here
volumes:
  postgres_data:
  redis_data:
  backend_logs:
  backend_uploads:
  media_files:
  celery_logs:
  flower_logs:

networks:
  topworx_network:
    driver: bridge
COMPOSE_EOF

print_message "docker-compose.yml ایجاد شد"

# ── مرحله 5: Dockerfile‌ها ─────────────────────────────────────────────────
print_header "مرحله 5: ایجاد Dockerfile ها"

mkdir -p backend topworx-new

# Backend Dockerfile (only written if one doesn't exist already)
if [ ! -f backend/Dockerfile ]; then
cat > backend/Dockerfile << 'DOCKERFILE_BACKEND'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE_BACKEND
    print_message "backend/Dockerfile ایجاد شد"
else
    print_warning "backend/Dockerfile از قبل وجود دارد — رد شد"
fi

# Frontend Dockerfile (only written if one doesn't exist already)
if [ ! -f topworx-new/Dockerfile ]; then
cat > topworx-new/Dockerfile << 'DOCKERFILE_FRONTEND'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
# --network=host lets npm reach the internet using the host's DNS
RUN --network=host npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
DOCKERFILE_FRONTEND

cat > topworx-new/nginx.conf << 'NGINX_FRONTEND'
server {
    listen 3000;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /health {
        return 200 "ok";
        add_header Content-Type text/plain;
    }
}
NGINX_FRONTEND
    print_message "topworx-new/Dockerfile ایجاد شد"
else
    print_warning "topworx-new/Dockerfile از قبل وجود دارد — رد شد"
fi

# ── مرحله 6: Nginx اصلی ──────────────────────────────────────────────────────
print_header "مرحله 6: تنظیم Nginx"

# The nginx config uses $DOMAIN which IS a shell variable — no quotes on heredoc
# delimiter so it expands now (we want the actual IP/domain in the file).
# Nginx variables like $host and $remote_addr are escaped with \$ to survive.
cat > nginx/nginx.conf << NGINX_MAIN
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile      on;
    keepalive_timeout 65;
    client_max_body_size 50M;

    upstream backend_upstream {
        server backend:8000;
    }

    upstream frontend_upstream {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name ${DOMAIN};

        # Backend API — strip /api prefix before forwarding
        location /api/ {
            proxy_pass         http://backend_upstream/;
            proxy_http_version 1.1;
            proxy_set_header   Host              \$host;
            proxy_set_header   X-Real-IP         \$remote_addr;
            proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto \$scheme;
            proxy_read_timeout 300s;
        }

        # Serve uploaded media files directly
        location /media/ {
            alias /var/www/media/;
            expires 7d;
            add_header Cache-Control "public, immutable";
        }

        # Everything else → frontend
        location / {
            proxy_pass         http://frontend_upstream;
            proxy_http_version 1.1;
            proxy_set_header   Host              \$host;
            proxy_set_header   X-Real-IP         \$remote_addr;
            proxy_set_header   Upgrade           \$http_upgrade;
            proxy_set_header   Connection        "upgrade";
        }
    }
}
NGINX_MAIN

print_message "nginx/nginx.conf ایجاد شد"

# ── مرحله 7: ساخت و راه‌اندازی ───────────────────────────────────────────────
print_header "مرحله 7: ساخت و راه‌اندازی"
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

print_message "ساخت Docker images..."
if ! docker compose build --no-cache \
    --build-arg BUILDKIT_INLINE_CACHE=0; then
    print_error "ساخت Docker images ناموفق بود!"
    print_warning "بررسی کنید: docker compose logs"
    exit 1
fi

print_message "راه‌اندازی سرویس‌ها..."
if ! docker compose up -d; then
    print_error "راه‌اندازی سرویس‌ها ناموفق بود!"
    print_warning "بررسی کنید: docker compose ps && docker compose logs"
    exit 1
fi

print_message "انتظار برای آماده شدن سرویس‌ها (30 ثانیه)..."
sleep 30

docker compose ps

# ── خلاصه نصب ────────────────────────────────────────────────────────────────
print_header "نصب TOP WorX کامل شد!"
echo ""
echo -e "${GREEN}اطلاعات دسترسی:${NC}"
echo -e "  Frontend:   http://${DOMAIN}"
echo -e "  Backend API: http://${DOMAIN}/api"
echo -e "  Flower:     http://${DOMAIN}:5555  (فقط از localhost)"
echo ""
echo -e "${YELLOW}رمزهای عبور تولید شده (در فایل .env ذخیره شدند):${NC}"
echo -e "  PostgreSQL:  ${POSTGRES_PASSWORD}"
echo -e "  Redis:       ${REDIS_PASSWORD}"
echo -e "  Grafana:     ${GRAFANA_PASSWORD}"
echo -e "  Flower:      ${FLOWER_PASSWORD}  (user: admin)"
echo ""
echo -e "${RED}هشدار: فایل .env حاوی اطلاعات حساس است. آن را در مخزن git قرار ندهید!${NC}"