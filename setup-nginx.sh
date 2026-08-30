#!/bin/bash

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_header "تنظیم Nginx برای TOP WorX"

# درخواست دامنه از کاربر
echo -n "دامنه یا IP سرور را وارد کنید (مثال: topworx.local یا 192.168.1.100): "
read DOMAIN

# پشتیبان‌گیری از تنظیمات اصلی
print_message "پشتیبان‌گیری از تنظیمات Nginx..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# تنظیم nginx.conf اصلی
print_message "تنظیم Nginx برای عملکرد بهتر..."

sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # تنظیمات پایه
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # تنظیمات MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # تنظیمات لاگ
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # تنظیمات Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # تنظیمات امنیتی
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # تنظیمات Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # تنظیمات Upstream
    upstream backend {
        server 127.0.0.1:8000;
        keepalive 32;
    }

    upstream frontend {
        server 127.0.0.1:3000;
        keepalive 32;
    }

    # تنظیمات سرور
    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        # تنظیمات SSL (برای توسعه)
        ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
        ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # تنظیمات امنیتی اضافی
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend (React App)
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 86400;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300;
            proxy_connect_timeout 75;
        }

        # Static Files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Media Files
        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # Health Check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Security Headers
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header X-Content-Type-Options nosniff;
        }
    }
}
EOF

# ایجاد فایل تنظیمات مخصوص TOP WorX
print_message "ایجاد فایل تنظیمات مخصوص TOP WorX..."

sudo tee /etc/nginx/sites-available/topworx > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Rate Limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=1r/s;

    # Frontend (React App)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 75;
    }

    # Static Files
    location /static/ {
        alias /var/www/topworx/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/topworx/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health Check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Security Headers for Static Files
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
    }
}
EOF

# ایجاد دایرکتوری‌های مورد نیاز
print_message "ایجاد دایرکتوری‌های مورد نیاز..."
sudo mkdir -p /var/www/topworx/static
sudo mkdir -p /var/www/topworx/media
sudo chown -R www-data:www-data /var/www/topworx

# فعال‌سازی سایت
print_message "فعال‌سازی سایت TOP WorX..."
sudo ln -sf /etc/nginx/sites-available/topworx /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# تست تنظیمات Nginx
print_message "تست تنظیمات Nginx..."
if sudo nginx -t; then
    print_message "تنظیمات Nginx صحیح است"
else
    print_error "خطا در تنظیمات Nginx"
    exit 1
fi

# راه‌اندازی مجدد Nginx
print_message "راه‌اندازی مجدد Nginx..."
sudo systemctl reload nginx

# بررسی وضعیت سرویس
if sudo systemctl is-active --quiet nginx; then
    print_message "Nginx با موفقیت راه‌اندازی شد"
else
    print_error "خطا در راه‌اندازی Nginx"
    exit 1
fi

# نمایش اطلاعات
print_message "اطلاعات Nginx:"
echo "Domain: $DOMAIN"
echo "Frontend Port: 3000"
echo "Backend Port: 8000"
echo "SSL: Enabled (Self-signed for development)"
echo "Static Files: /var/www/topworx/static"
echo "Media Files: /var/www/topworx/media"

print_warning "برای تولید، لطفاً گواهی SSL معتبر نصب کنید"

print_header "تنظیم Nginx کامل شد" 