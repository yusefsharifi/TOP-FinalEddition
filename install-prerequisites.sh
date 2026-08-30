#!/bin/bash

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# تابع نمایش پیام
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

# بررسی اینکه آیا کاربر root است
if [ "$EUID" -eq 0 ]; then
    print_error "لطفاً این اسکریپت را به عنوان کاربر عادی اجرا کنید، نه root"
    exit 1
fi

print_header "نصب پیش‌نیازهای TOP WorX ERP System"

# به‌روزرسانی سیستم
print_message "به‌روزرسانی سیستم..."
sudo apt update && sudo apt upgrade -y

# نصب ابزارهای پایه
print_message "نصب ابزارهای پایه..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# نصب Python 3.11
print_message "نصب Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# تأیید نصب Python
if command -v python3.11 &> /dev/null; then
    print_message "Python 3.11 با موفقیت نصب شد: $(python3.11 --version)"
else
    print_error "خطا در نصب Python 3.11"
    exit 1
fi

# نصب PostgreSQL 15
print_message "نصب PostgreSQL 15..."
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15

# راه‌اندازی PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# ایجاد کاربر و دیتابیس
print_message "تنظیم دیتابیس PostgreSQL..."
sudo -u postgres createuser --interactive topworx --pwprompt
sudo -u postgres createdb topworx_db
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE topworx_db TO topworx;"

# نصب Redis
print_message "نصب Redis..."
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# تست Redis
if redis-cli ping | grep -q "PONG"; then
    print_message "Redis با موفقیت نصب و راه‌اندازی شد"
else
    print_error "خطا در راه‌اندازی Redis"
    exit 1
fi

# نصب Node.js 18 LTS
print_message "نصب Node.js 18 LTS..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# تأیید نصب Node.js
if command -v node &> /dev/null; then
    print_message "Node.js با موفقیت نصب شد: $(node --version)"
    print_message "npm با موفقیت نصب شد: $(npm --version)"
else
    print_error "خطا در نصب Node.js"
    exit 1
fi

# نصب Yarn
print_message "نصب Yarn..."
sudo npm install -g yarn

# نصب Docker و Docker Compose
print_message "نصب Docker و Docker Compose..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# راه‌اندازی Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# تأیید نصب Docker
if command -v docker &> /dev/null; then
    print_message "Docker با موفقیت نصب شد: $(docker --version)"
else
    print_error "خطا در نصب Docker"
    exit 1
fi

# نصب Nginx
print_message "نصب Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# نصب ابزارهای امنیتی
print_message "نصب ابزارهای امنیتی..."
sudo apt install -y fail2ban ufw

# تنظیم فایروال
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3000  # React App
sudo ufw allow 8000  # FastAPI Backend

# نصب ابزارهای توسعه
print_message "نصب ابزارهای توسعه..."
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev htop tree tmux

# نصب ابزارهای مانیتورینگ
print_message "نصب ابزارهای مانیتورینگ..."
sudo apt install -y htop iotop nethogs

print_header "نصب پیش‌نیازها کامل شد"

# نمایش اطلاعات نصب
echo ""
print_message "اطلاعات نصب:"
echo "Python 3.11: $(python3.11 --version)"
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "PostgreSQL: $(psql --version)"
echo "Redis: $(redis-server --version | head -n1)"
echo "Nginx: $(nginx -v 2>&1)"

echo ""
print_warning "برای اعمال تغییرات Docker، لطفاً سیستم را restart کنید:"
echo "sudo reboot"

echo ""
print_message "مراحل بعدی:"
echo "1. سیستم را restart کنید"
echo "2. فایل docker-compose.yml را تنظیم کنید"
echo "3. متغیرهای محیطی را در فایل .env تنظیم کنید"
echo "4. دستور docker-compose up -d را اجرا کنید"

print_header "نصب پیش‌نیازهای TOP WorX کامل شد" 