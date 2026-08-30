"""تعریف الگوها و ثابت‌های مورد استفاده در تحلیل محتوا"""

# الگوهای تاریخ
DATE_PATTERNS = [
    r'\d{1,2}/\d{1,2}/\d{2,4}',
    r'\d{1,2}-\d{1,2}-\d{2,4}',
    r'\d{4}-\d{2}-\d{2}',
    r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}'
]

# الگوهای معیار
METRIC_PATTERNS = [
    r'sales',
    r'revenue',
    r'profit',
    r'cost',
    r'quantity',
    r'percentage',
    r'growth',
    r'rate'
]

# کلمات مثبت برای تحلیل احساسات
POSITIVE_WORDS = {
    "good", "great", "excellent", "positive", "happy", "satisfied",
    "perfect", "amazing", "wonderful", "fantastic", "brilliant",
    "عالی", "خوب", "ممتاز", "مثبت", "خوشحال", "راضی",
    "کامل", "شگفت‌انگیز", "عالی", "فوق‌العاده", "درخشان"
}

# کلمات منفی برای تحلیل احساسات
NEGATIVE_WORDS = {
    "bad", "poor", "negative", "unhappy", "terrible", "awful",
    "horrible", "disappointing", "frustrating", "annoying", "problem",
    "بد", "ضعیف", "منفی", "ناراحت", "وحشتناک", "بد",
    "مخوف", "ناامیدکننده", "خسته‌کننده", "آزاردهنده", "مشکل"
}

# کلمات فوری برای تحلیل فوریت
URGENT_WORDS = {
    "urgent", "immediate", "asap", "critical", "important",
    "priority", "emergency", "quick", "fast", "now",
    "فوری", "فوراً", "همین حالا", "حیاتی", "مهم",
    "اولویت", "اورژانسی", "سریع", "تند", "الان"
}

# کلمات غیرفوری برای تحلیل فوریت
NON_URGENT_WORDS = {
    "whenever", "later", "sometime", "optional", "flexible",
    "convenient", "when possible", "no rush",
    "هر وقت", "بعداً", "گاهی", "اختیاری", "انعطاف‌پذیر",
    "مناسب", "وقتی ممکن است", "عجله‌ای نیست"
}

# اعمال رایج در دستورات
COMMON_ACTIONS = {
    "generate": ["generate", "create", "make", "produce", "ایجاد", "ساخت", "تولید"],
    "update": ["update", "modify", "change", "edit", "به‌روزرسانی", "تغییر", "ویرایش"],
    "delete": ["delete", "remove", "erase", "clear", "حذف", "پاک", "مخفی"],
    "analyze": ["analyze", "examine", "investigate", "study", "تحلیل", "بررسی", "مطالعه"],
    "report": ["report", "show", "display", "present", "گزارش", "نمایش", "ارائه"],
    "export": ["export", "download", "save", "extract", "خروجی", "دانلود", "ذخیره"],
    "import": ["import", "upload", "load", "add", "ورودی", "بارگذاری", "افزودن"]
}

# اهداف رایج در دستورات
COMMON_TARGETS = {
    "report": ["report", "گزارش"],
    "data": ["data", "داده"],
    "information": ["information", "اطلاعات"],
    "summary": ["summary", "خلاصه"],
    "analysis": ["analysis", "تحلیل"]
}

# نشانگرهای عمل در متن
ACTION_INDICATORS = {
    "want": "generate",
    "need": "generate",
    "show": "report",
    "display": "report",
    "calculate": "calculate",
    "summarize": "report",
    "می‌خواهم": "generate",
    "نیازم": "generate",
    "نمایش": "report",
    "نشان": "report",
    "محاسبه": "calculate",
    "خلاصه": "report"
}

# فرمت‌های پشتیبانی شده
SUPPORTED_FORMATS = ["json", "csv", "excel", "pdf", "html"] 