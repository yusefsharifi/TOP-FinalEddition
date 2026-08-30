import unittest
from typing import Dict, List, Callable, Any
import inspect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DynamicTestManager:
    def __init__(self):
        self.test_cases: Dict[str, List[Dict]] = {}
        self.test_results: Dict[str, List[Dict]] = {}
        self.test_history: List[Dict] = []

    def add_test_case(self, category: str, test_name: str, test_func: Callable, 
                     description: str = "", tags: List[str] = None) -> None:
        """
        اضافه کردن یک تست جدید به سیستم
        
        Args:
            category: دسته‌بندی تست (مثلاً: survey, customer, notification)
            test_name: نام تست
            test_func: تابع تست
            description: توضیحات تست
            tags: برچسب‌های تست
        """
        if category not in self.test_cases:
            self.test_cases[category] = []
        
        test_case = {
            "name": test_name,
            "function": test_func,
            "description": description,
            "tags": tags or [],
            "added_at": datetime.utcnow()
        }
        
        self.test_cases[category].append(test_case)
        logger.info(f"تست جدید اضافه شد: {category}.{test_name}")

    def run_test(self, category: str, test_name: str, **kwargs) -> Dict:
        """
        اجرای یک تست خاص
        
        Args:
            category: دسته‌بندی تست
            test_name: نام تست
            **kwargs: پارامترهای اضافی برای تست
            
        Returns:
            نتیجه تست
        """
        if category not in self.test_cases:
            raise ValueError(f"دسته‌بندی تست یافت نشد: {category}")
            
        test_case = next(
            (tc for tc in self.test_cases[category] if tc["name"] == test_name),
            None
        )
        
        if not test_case:
            raise ValueError(f"تست یافت نشد: {category}.{test_name}")
            
        try:
            start_time = datetime.utcnow()
            result = test_case["function"](**kwargs)
            end_time = datetime.utcnow()
            
            test_result = {
                "category": category,
                "name": test_name,
                "status": "success",
                "result": result,
                "start_time": start_time,
                "end_time": end_time,
                "duration": (end_time - start_time).total_seconds()
            }
            
            if category not in self.test_results:
                self.test_results[category] = []
            self.test_results[category].append(test_result)
            self.test_history.append(test_result)
            
            return test_result
            
        except Exception as e:
            error_result = {
                "category": category,
                "name": test_name,
                "status": "error",
                "error": str(e),
                "start_time": datetime.utcnow(),
                "end_time": datetime.utcnow()
            }
            
            if category not in self.test_results:
                self.test_results[category] = []
            self.test_results[category].append(error_result)
            self.test_history.append(error_result)
            
            raise

    def run_category_tests(self, category: str, **kwargs) -> List[Dict]:
        """
        اجرای تمام تست‌های یک دسته‌بندی
        
        Args:
            category: دسته‌بندی تست
            **kwargs: پارامترهای اضافی برای تست‌ها
            
        Returns:
            لیست نتایج تست‌ها
        """
        if category not in self.test_cases:
            raise ValueError(f"دسته‌بندی تست یافت نشد: {category}")
            
        results = []
        for test_case in self.test_cases[category]:
            try:
                result = self.run_test(category, test_case["name"], **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"خطا در اجرای تست {category}.{test_case['name']}: {str(e)}")
                results.append({
                    "category": category,
                    "name": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results

    def get_test_cases(self, category: str = None) -> Dict:
        """
        دریافت لیست تست‌ها
        
        Args:
            category: دسته‌بندی تست (اختیاری)
            
        Returns:
            دیکشنری تست‌ها
        """
        if category:
            return self.test_cases.get(category, {})
        return self.test_cases

    def get_test_results(self, category: str = None) -> Dict:
        """
        دریافت نتایج تست‌ها
        
        Args:
            category: دسته‌بندی تست (اختیاری)
            
        Returns:
            دیکشنری نتایج
        """
        if category:
            return self.test_results.get(category, {})
        return self.test_results

    def get_test_history(self, limit: int = None) -> List[Dict]:
        """
        دریافت تاریخچه تست‌ها
        
        Args:
            limit: تعداد نتایج (اختیاری)
            
        Returns:
            لیست تاریخچه
        """
        if limit:
            return self.test_history[-limit:]
        return self.test_history

    def clear_test_history(self) -> None:
        """پاک کردن تاریخچه تست‌ها"""
        self.test_history = []

    def get_test_statistics(self) -> Dict:
        """
        دریافت آمار تست‌ها
        
        Returns:
            دیکشنری آمار
        """
        total_tests = sum(len(tests) for tests in self.test_cases.values())
        total_results = len(self.test_history)
        success_count = sum(1 for r in self.test_history if r["status"] == "success")
        error_count = sum(1 for r in self.test_history if r["status"] == "error")
        
        return {
            "total_tests": total_tests,
            "total_results": total_results,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": (success_count / total_results * 100) if total_results > 0 else 0
        } 