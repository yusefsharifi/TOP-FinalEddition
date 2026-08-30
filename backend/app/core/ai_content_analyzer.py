import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from transformers import pipeline
import spacy
import re
from decimal import Decimal

from .ai_patterns import (
    DATE_PATTERNS,
    METRIC_PATTERNS,
    POSITIVE_WORDS,
    NEGATIVE_WORDS,
    URGENT_WORDS,
    NON_URGENT_WORDS,
    COMMON_ACTIONS,
    COMMON_TARGETS,
    ACTION_INDICATORS,
    SUPPORTED_FORMATS
)

class AIContentAnalyzer:
    """کلاس تحلیل محتوای هوشمند"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # راه‌اندازی مدل‌های پردازش زبان طبیعی
        self.nlp = spacy.load("en_core_web_sm")
        self.ner_model = pipeline("ner")
        self.zero_shot_classifier = pipeline("zero-shot-classification")
        
        # تعریف الگوها
        self.date_patterns = DATE_PATTERNS
        self.metric_patterns = METRIC_PATTERNS
        
        # تعریف مجموعه‌های کلمات
        self.positive_words = POSITIVE_WORDS
        self.negative_words = NEGATIVE_WORDS
        self.urgent_words = URGENT_WORDS
        self.non_urgent_words = NON_URGENT_WORDS
        
        # تعریف اعمال و اهداف
        self.common_actions = COMMON_ACTIONS
        self.common_targets = COMMON_TARGETS
        self.action_indicators = ACTION_INDICATORS
        
        # تعریف فرمت‌ها
        self.supported_formats = SUPPORTED_FORMATS
    
    def extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """استخراج موجودیت‌های نام‌دار از متن با استفاده از spaCy و مدل NER"""
        try:
            entities = []
            
            # استخراج موجودیت‌ها با استفاده از spaCy
            doc = self.nlp(content)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            # استخراج موجودیت‌ها با استفاده از مدل NER
            ner_results = self.ner_model(content)
            for result in ner_results:
                entities.append({
                    'text': result['word'],
                    'label': result['entity'],
                    'start': result['start'],
                    'end': result['end']
                })
            
            return entities
        except Exception as e:
            self.logger.error(f"خطا در استخراج موجودیت‌ها: {str(e)}")
            return []
    
    def calculate_suggestion_confidence(self, content: str) -> float:
        """محاسبه امتیاز اعتماد برای پیشنهاد با استفاده از طبقه‌بندی صفر-شات"""
        try:
            # تعریف دسته‌بندی‌های پیشنهاد
            categories = [
                "feature request",
                "improvement",
                "bug report",
                "general feedback"
            ]
            
            # طبقه‌بندی محتوا
            result = self.zero_shot_classifier(content, categories)
            
            # محاسبه اعتماد بر اساس امتیازهای طبقه‌بندی
            confidence = max(result['scores'])
            
            return confidence
        except Exception as e:
            self.logger.error(f"خطا در محاسبه اعتماد پیشنهاد: {str(e)}")
            return 0.0
    
    def calculate_feedback_impact(self, content: str) -> float:
        """محاسبه امتیاز تأثیر بازخورد با استفاده از عوامل متعدد"""
        try:
            # تحلیل احساسات
            doc = self.nlp(content)
            sentiment_score = self.analyze_sentiment(doc)
            
            # تحلیل فوریت
            urgency_score = self.analyze_urgency(doc)
            
            # تحلیل دامنه
            scope_score = self.analyze_scope(doc)
            
            # محاسبه امتیاز تأثیر وزنی
            impact = (
                sentiment_score * 0.4 +
                urgency_score * 0.3 +
                scope_score * 0.3
            )
            
            return impact
        except Exception as e:
            self.logger.error(f"خطا در محاسبه تأثیر بازخورد: {str(e)}")
            return 0.0
    
    def analyze_sentiment(self, doc) -> float:
        """تحلیل احساسات متن با استفاده از الگوهای کلمه"""
        try:
            sentiment = 0.0
            for token in doc:
                if token.text.lower() in self.positive_words:
                    sentiment += 0.2
                elif token.text.lower() in self.negative_words:
                    sentiment -= 0.2
            
            return max(0.0, min(1.0, sentiment + 0.5))
        except Exception as e:
            self.logger.error(f"خطا در تحلیل احساسات: {str(e)}")
            return 0.5
    
    def analyze_urgency(self, doc) -> float:
        """تحلیل فوریت متن با استفاده از الگوهای کلمه"""
        try:
            urgency = 0.0
            for token in doc:
                if token.text.lower() in self.urgent_words:
                    urgency += 0.3
                elif token.text.lower() in self.non_urgent_words:
                    urgency -= 0.3
            
            return max(0.0, min(1.0, urgency + 0.5))
        except Exception as e:
            self.logger.error(f"خطا در تحلیل فوریت: {str(e)}")
            return 0.5
    
    def analyze_scope(self, doc) -> float:
        """تحلیل دامنه متن با استفاده از تشخیص موجودیت"""
        try:
            # شمارش موجودیت‌های نام‌دار به عنوان معیار دامنه
            entity_count = len([ent for ent in doc.ents])
            
            # نرمال‌سازی امتیاز دامنه
            scope = min(1.0, entity_count / 10.0)
            
            return scope
        except Exception as e:
            self.logger.error(f"خطا در تحلیل دامنه: {str(e)}")
            return 0.5 