import logging
import sys
from pathlib import Path

# ساخت پوشه لاگ
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# تنظیم لاگ فرمت
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# فایل Handler
file_handler = logging.FileHandler(log_dir / "app.log")
file_handler.setFormatter(formatter)

# کنسول Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# روت لاگر
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)