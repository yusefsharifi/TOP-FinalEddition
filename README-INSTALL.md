# راهنمای نصب TOP WorX ERP System

## مقدمه

TOP WorX یک سیستم ERP پیشرفته و جامع است که شامل بیش از 20 ماژول مختلف برای مدیریت کامل کسب و کار می‌باشد. این راهنما مراحل نصب و راه‌اندازی سیستم را روی Ubuntu توضیح می‌دهد.

## پیش‌نیازها

### سیستم عامل
- Ubuntu 20.04 LTS یا بالاتر
- حداقل 4GB RAM
- حداقل 50GB فضای دیسک
- دسترسی sudo

### نرم‌افزارهای مورد نیاز
- Python 3.11
- Node.js 18 LTS
- PostgreSQL 15
- Redis 7
- Docker & Docker Compose
- Nginx
- Git

## مراحل نصب

### مرحله 1: دانلود پروژه

```bash
# کلون کردن repository
git clone https://github.com/your-username/topworx.git
cd topworx

# اعطای مجوز اجرا به اسکریپت‌ها
chmod +x *.sh
```

### مرحله 2: نصب خودکار (توصیه شده)

برای نصب کامل و خودکار، اسکریپت اصلی را اجرا کنید:

```bash
./install.sh
```

این اسکریپت تمام مراحل زیر را به صورت خودکار انجام می‌دهد.

### مرحله 3: نصب دستی (اختیاری)

اگر می‌خواهید مراحل را به صورت دستی انجام دهید:

#### 3.1 نصب پیش‌نیازها
```bash
./install-prerequisites.sh
```

#### 3.2 تنظیم PostgreSQL
```bash
./setup-postgresql.sh
```

#### 3.3 تنظیم Nginx
```bash
./setup-nginx.sh
```

#### 3.4 تنظیم امنیتی
```bash
./setup-security.sh
```

### مرحله 4: تنظیم متغیرهای محیطی

```bash
# کپی کردن فایل نمونه
cp env.example .env

# ویرایش فایل .env
nano .env
```

مقادیر مهم که باید تغییر دهید:
- `POSTGRES_PASSWORD`: رمز عبور دیتابیس
- `REDIS_PASSWORD`: رمز عبور Redis
- `SECRET_KEY`: کلید امنیتی (حداقل 32 کاراکتر)
- `DOMAIN`: دامنه یا IP سرور

### مرحله 5: راه‌اندازی سرویس‌ها

```bash
# ساخت Docker images
docker-compose build

# راه‌اندازی سرویس‌ها
docker-compose up -d

# بررسی وضعیت
docker-compose ps
```

## ماژول‌های سیستم

TOP WorX شامل ماژول‌های زیر است:

### ماژول‌های اصلی
1. **Dashboard** - داشبورد مدیریتی
2. **CRM** - مدیریت روابط مشتریان
3. **Inventory** - مدیریت انبار و کالا
4. **Finance** - مدیریت مالی
5. **Accounting** - حسابداری
6. **HR** - مدیریت منابع انسانی
7. **Sales** - مدیریت فروش
8. **Purchase** - مدیریت خرید
9. **Procurement** - تأمین و خرید
10. **Quality** - مدیریت کیفیت

### ماژول‌های پیشرفته
11. **Projects** - مدیریت پروژه
12. **BI** - هوش تجاری
13. **AI** - هوش مصنوعی
14. **Reports** - گزارشات
15. **Tasks** - مدیریت وظایف
16. **Correspondence** - نامه‌نگاری
17. **HSE** - سلامت، ایمنی و محیط زیست
18. **Calendar** - تقویم
19. **Documents** - مدیریت مستندات
20. **Settings** - تنظیمات
21. **Security** - امنیت و دسترسی‌ها

## دسترسی به سیستم

پس از نصب موفق، می‌توانید از طریق آدرس‌های زیر به سیستم دسترسی داشته باشید:

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Nginx Proxy**: http://localhost
- **Grafana Dashboard**: http://localhost:3001
- **Prometheus Monitoring**: http://localhost:9090
- **Kibana Logs**: http://localhost:5601

## کاربران پیش‌فرض

### Super Admin
- **Username**: superadmin
- **Password**: (در طول نصب تنظیم می‌شود)
- **دسترسی**: تمام ماژول‌ها

### کاربران ادمین ماژول‌ها
- **CRM Admin**: crm_admin
- **Finance Admin**: finance_admin
- **HR Admin**: hr_admin
- **Inventory Admin**: inventory_admin

## مدیریت سیستم

### دستورات مفید Docker Compose

```bash
# مشاهده وضعیت سرویس‌ها
docker-compose ps

# مشاهده لاگ‌ها
docker-compose logs -f

# راه‌اندازی مجدد سرویس خاص
docker-compose restart backend

# توقف تمام سرویس‌ها
docker-compose down

# راه‌اندازی مجدد تمام سرویس‌ها
docker-compose restart

# پشتیبان‌گیری از دیتابیس
docker-compose run --rm backup
```

### مدیریت لاگ‌ها

```bash
# مشاهده لاگ‌های Backend
docker-compose logs -f backend

# مشاهده لاگ‌های Frontend
docker-compose logs -f frontend

# مشاهده لاگ‌های Nginx
docker-compose logs -f nginx

# مشاهده لاگ‌های PostgreSQL
docker-compose logs -f postgres
```

### پشتیبان‌گیری و بازیابی

```bash
# پشتیبان‌گیری خودکار (روزانه)
# در cron job تنظیم شده است

# پشتیبان‌گیری دستی
docker-compose run --rm backup

# بازیابی از پشتیبان
docker-compose exec postgres psql -U topworx -d topworx_db < backup_file.sql
```

## امنیت

### تنظیمات امنیتی اعمال شده
- فایروال UFW فعال
- Fail2ban برای محافظت از حملات
- SSL/TLS encryption
- Rate limiting
- Security headers
- Audit trail

### توصیه‌های امنیتی
1. رمزهای عبور قوی تنظیم کنید
2. گواهی SSL معتبر نصب کنید
3. به‌روزرسانی‌های امنیتی را نصب کنید
4. لاگ‌ها را به طور منظم بررسی کنید
5. پشتیبان‌گیری منظم انجام دهید

## مانیتورینگ

### Grafana Dashboards
- سیستم monitoring
- عملکرد دیتابیس
- لاگ‌های سیستم
- آمار کاربران

### Prometheus Metrics
- CPU و Memory usage
- Network traffic
- Database performance
- Application metrics

### Kibana Logs
- لاگ‌های اپلیکیشن
- لاگ‌های سیستم
- لاگ‌های امنیتی
- Audit trail

## عیب‌یابی

### مشکلات رایج

#### 1. سرویس‌ها راه‌اندازی نمی‌شوند
```bash
# بررسی لاگ‌ها
docker-compose logs

# بررسی وضعیت کانتینرها
docker-compose ps

# راه‌اندازی مجدد
docker-compose down && docker-compose up -d
```

#### 2. مشکل اتصال به دیتابیس
```bash
# بررسی وضعیت PostgreSQL
docker-compose logs postgres

# تست اتصال
docker-compose exec postgres psql -U topworx -d topworx_db
```

#### 3. مشکل دسترسی به Frontend
```bash
# بررسی وضعیت React app
docker-compose logs frontend

# بررسی پورت‌ها
netstat -tuln | grep 3000
```

### لاگ‌های مهم
- `/var/log/nginx/error.log` - لاگ‌های Nginx
- `/var/log/postgresql/` - لاگ‌های PostgreSQL
- `/var/log/redis/` - لاگ‌های Redis
- `docker-compose logs` - لاگ‌های Docker

## به‌روزرسانی

### به‌روزرسانی سیستم
```bash
# دریافت آخرین تغییرات
git pull origin main

# بازسازی images
docker-compose build

# راه‌اندازی مجدد
docker-compose down && docker-compose up -d
```

### به‌روزرسانی دیتابیس
```bash
# اجرای migrations
docker-compose exec backend alembic upgrade head
```

## پشتیبانی

برای دریافت پشتیبانی:
- **مستندات**: [docs.topworx.com](https://docs.topworx.com)
- **GitHub Issues**: [github.com/topworx/issues](https://github.com/topworx/issues)
- **ایمیل**: support@topworx.com

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل LICENSE را مطالعه کنید.

---

**TOP WorX ERP System** - راه‌حل جامع مدیریت کسب و کار 