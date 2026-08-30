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

print_header "تنظیم PostgreSQL برای TOP WorX"

# پشتیبان‌گیری از فایل تنظیمات اصلی
print_message "پشتیبان‌گیری از تنظیمات PostgreSQL..."
sudo cp /etc/postgresql/15/main/postgresql.conf /etc/postgresql/15/main/postgresql.conf.backup

# ایجاد فایل تنظیمات بهینه
print_message "تنظیم PostgreSQL برای عملکرد بهتر..."

sudo tee /etc/postgresql/15/main/postgresql.conf > /dev/null << 'EOF'
# تنظیمات اتصال
listen_addresses = '*'
port = 5432
max_connections = 200

# تنظیمات حافظه
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB

# تنظیمات WAL
wal_buffers = 16MB
checkpoint_completion_target = 0.9
min_wal_size = 1GB
max_wal_size = 4GB

# تنظیمات آمار
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# تنظیمات لاگ
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = -1

# تنظیمات امنیتی
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'

# تنظیمات عملکرد
synchronous_commit = off
fsync = on
full_page_writes = on
EOF

# تنظیم pg_hba.conf برای اتصال محلی
print_message "تنظیم دسترسی‌های PostgreSQL..."

sudo tee /etc/postgresql/15/main/pg_hba.conf > /dev/null << 'EOF'
# تنظیمات دسترسی PostgreSQL
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF

# ایجاد دایرکتوری لاگ
sudo mkdir -p /var/log/postgresql
sudo chown postgres:postgres /var/log/postgresql

# راه‌اندازی مجدد PostgreSQL
print_message "راه‌اندازی مجدد PostgreSQL..."
sudo systemctl restart postgresql

# بررسی وضعیت سرویس
if sudo systemctl is-active --quiet postgresql; then
    print_message "PostgreSQL با موفقیت راه‌اندازی شد"
else
    print_error "خطا در راه‌اندازی PostgreSQL"
    exit 1
fi

# ایجاد کاربر و دیتابیس برای TOP WorX
print_message "ایجاد کاربر و دیتابیس TOP WorX..."

# درخواست رمز عبور از کاربر
echo -n "رمز عبور برای کاربر topworx را وارد کنید: "
read -s TOPWORX_PASSWORD
echo

# ایجاد کاربر
sudo -u postgres psql -c "CREATE USER topworx WITH PASSWORD '$TOPWORX_PASSWORD';" 2>/dev/null || echo "کاربر topworx قبلاً وجود دارد"

# ایجاد دیتابیس
sudo -u postgres createdb topworx_db 2>/dev/null || echo "دیتابیس topworx_db قبلاً وجود دارد"

# اعطای دسترسی‌ها
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE topworx_db TO topworx;"
sudo -u postgres psql -c "ALTER USER topworx CREATEDB;"
sudo -u postgres psql -c "ALTER USER topworx SUPERUSER;"

# تست اتصال
print_message "تست اتصال به دیتابیس..."
if PGPASSWORD=$TOPWORX_PASSWORD psql -h localhost -U topworx -d topworx_db -c "SELECT version();" > /dev/null 2>&1; then
    print_message "اتصال به دیتابیس موفقیت‌آمیز بود"
else
    print_error "خطا در اتصال به دیتابیس"
    exit 1
fi

# نمایش اطلاعات دیتابیس
print_message "اطلاعات دیتابیس:"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: topworx_db"
echo "Username: topworx"
echo "Password: [مخفی]"

print_header "تنظیم PostgreSQL کامل شد" 