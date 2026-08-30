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

print_header "تنظیم امنیتی برای TOP WorX"

# تنظیم UFW Firewall
print_message "تنظیم فایروال UFW..."

# فعال‌سازی UFW
sudo ufw --force enable

# تنظیم قوانین پیش‌فرض
sudo ufw default deny incoming
sudo ufw default allow outgoing

# باز کردن پورت‌های ضروری
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp  # React App
sudo ufw allow 8000/tcp  # FastAPI Backend
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 6379/tcp  # Redis

# نمایش وضعیت فایروال
print_message "وضعیت فایروال:"
sudo ufw status verbose

# تنظیم Fail2ban
print_message "تنظیم Fail2ban..."

# ایجاد فایل تنظیمات مخصوص TOP WorX
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = auto

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[postgresql]
enabled = true
filter = postgresql
logpath = /var/log/postgresql/postgresql-15-main.log
maxretry = 3

[redis]
enabled = true
filter = redis
logpath = /var/log/redis/redis-server.log
maxretry = 3
EOF

# راه‌اندازی مجدد Fail2ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# تنظیمات امنیتی سیستم
print_message "تنظیمات امنیتی سیستم..."

# غیرفعال‌سازی SSH root login
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# تغییر پورت SSH (اختیاری)
echo -n "آیا می‌خواهید پورت SSH را تغییر دهید؟ (y/n): "
read CHANGE_SSH_PORT

if [ "$CHANGE_SSH_PORT" = "y" ] || [ "$CHANGE_SSH_PORT" = "Y" ]; then
    echo -n "پورت جدید SSH را وارد کنید (مثال: 2222): "
    read SSH_PORT
    sudo sed -i "s/#Port 22/Port $SSH_PORT/" /etc/ssh/sshd_config
    sudo ufw allow $SSH_PORT/tcp
    print_warning "پورت SSH به $SSH_PORT تغییر یافت. لطفاً مراقب باشید!"
fi

# راه‌اندازی مجدد SSH
sudo systemctl restart ssh

# تنظیمات امنیتی اضافی
print_message "تنظیمات امنیتی اضافی..."

# غیرفعال‌سازی سرویس‌های غیرضروری
sudo systemctl disable cups
sudo systemctl disable avahi-daemon
sudo systemctl disable bluetooth

# تنظیم محدودیت‌های سیستم
sudo tee /etc/security/limits.conf > /dev/null << 'EOF'
# محدودیت‌های امنیتی
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF

# تنظیم sysctl برای امنیت
print_message "تنظیم sysctl برای امنیت..."

sudo tee /etc/sysctl.conf > /dev/null << 'EOF'
# تنظیمات امنیتی شبکه
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
net.ipv4.route.flush = 1

# تنظیمات امنیتی ICMP
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# تنظیمات امنیتی TCP
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# تنظیمات امنیتی IPv6
net.ipv6.conf.all.accept_ra = 0
net.ipv6.conf.default.accept_ra = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0
EOF

# اعمال تنظیمات sysctl
sudo sysctl -p

# ایجاد کاربر ادمین برای TOP WorX
print_message "ایجاد کاربر ادمین برای TOP WorX..."

# درخواست اطلاعات کاربر
echo -n "نام کاربری ادمین TOP WorX را وارد کنید: "
read ADMIN_USERNAME

echo -n "نام کامل ادمین را وارد کنید: "
read ADMIN_FULLNAME

# ایجاد کاربر
sudo useradd -m -s /bin/bash -c "$ADMIN_FULLNAME" $ADMIN_USERNAME

# تنظیم رمز عبور
echo -n "رمز عبور برای کاربر $ADMIN_USERNAME را وارد کنید: "
read -s ADMIN_PASSWORD
echo
echo "$ADMIN_USERNAME:$ADMIN_PASSWORD" | sudo chpasswd

# اضافه کردن کاربر به گروه‌های ضروری
sudo usermod -aG sudo,docker $ADMIN_USERNAME

# تنظیم SSH key (اختیاری)
echo -n "آیا می‌خواهید SSH key برای کاربر $ADMIN_USERNAME تنظیم کنید؟ (y/n): "
read SETUP_SSH_KEY

if [ "$SETUP_SSH_KEY" = "y" ] || [ "$SETUP_SSH_KEY" = "Y" ]; then
    sudo mkdir -p /home/$ADMIN_USERNAME/.ssh
    sudo chmod 700 /home/$ADMIN_USERNAME/.ssh
    
    echo -n "کلید عمومی SSH را وارد کنید: "
    read SSH_PUBLIC_KEY
    echo "$SSH_PUBLIC_KEY" | sudo tee /home/$ADMIN_USERNAME/.ssh/authorized_keys > /dev/null
    
    sudo chmod 600 /home/$ADMIN_USERNAME/.ssh/authorized_keys
    sudo chown -R $ADMIN_USERNAME:$ADMIN_USERNAME /home/$ADMIN_USERNAME/.ssh
fi

# تنظیمات امنیتی Docker
print_message "تنظیمات امنیتی Docker..."

# ایجاد فایل تنظیمات Docker daemon
sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
EOF

# راه‌اندازی مجدد Docker
sudo systemctl restart docker

# تنظیمات امنیتی PostgreSQL
print_message "تنظیمات امنیتی PostgreSQL..."

# ایجاد فایل تنظیمات امنیتی PostgreSQL
sudo tee /etc/postgresql/15/main/conf.d/security.conf > /dev/null << 'EOF'
# تنظیمات امنیتی PostgreSQL
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
ssl_prefer_server_ciphers = on
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_min_protocol_version = 'TLSv1.2'

# محدودیت اتصالات
max_connections = 100

# تنظیمات لاگ امنیتی
log_connections = on
log_disconnections = on
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'all'
EOF

# راه‌اندازی مجدد PostgreSQL
sudo systemctl restart postgresql

# ایجاد فایل گزارش امنیتی
print_message "ایجاد گزارش امنیتی..."

sudo tee /usr/local/bin/security-report.sh > /dev/null << 'EOF'
#!/bin/bash

echo "=== گزارش امنیتی TOP WorX ==="
echo "تاریخ: $(date)"
echo ""

echo "=== وضعیت سرویس‌ها ==="
echo "SSH: $(systemctl is-active ssh)"
echo "UFW: $(systemctl is-active ufw)"
echo "Fail2ban: $(systemctl is-active fail2ban)"
echo "Docker: $(systemctl is-active docker)"
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Redis: $(systemctl is-active redis-server)"
echo "Nginx: $(systemctl is-active nginx)"
echo ""

echo "=== وضعیت فایروال ==="
sudo ufw status
echo ""

echo "=== لاگ‌های Fail2ban ==="
sudo fail2ban-client status
echo ""

echo "=== اتصالات فعال ==="
netstat -tuln | grep LISTEN
echo ""

echo "=== کاربران سیستم ==="
cat /etc/passwd | grep -E ":(0|1000):" | cut -d: -f1,3,7
echo ""

echo "=== فایل‌های حساس ==="
ls -la /etc/ssh/sshd_config
ls -la /etc/nginx/nginx.conf
ls -la /etc/postgresql/15/main/postgresql.conf
echo ""

echo "=== گزارش امنیتی کامل شد ==="
EOF

sudo chmod +x /usr/local/bin/security-report.sh

# نمایش اطلاعات نهایی
print_message "اطلاعات امنیتی:"
echo "Admin User: $ADMIN_USERNAME"
echo "SSH Port: $(grep '^Port' /etc/ssh/sshd_config | awk '{print $2}')"
echo "UFW Status: $(sudo ufw status | head -n1)"
echo "Fail2ban Status: $(sudo systemctl is-active fail2ban)"

print_warning "برای امنیت بیشتر:"
echo "1. گواهی SSL معتبر نصب کنید"
echo "2. رمزهای عبور قوی تنظیم کنید"
echo "3. به‌روزرسانی‌های امنیتی را نصب کنید"
echo "4. لاگ‌ها را به طور منظم بررسی کنید"

print_message "برای مشاهده گزارش امنیتی: /usr/local/bin/security-report.sh"

print_header "تنظیمات امنیتی کامل شد" 