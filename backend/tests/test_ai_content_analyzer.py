import unittest
from datetime import datetime
from app.core.ai_content_analyzer import AIContentAnalyzer

class TestAIContentAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = AIContentAnalyzer()
    
    def test_extract_entities(self):
        content = "John Smith works at Microsoft in New York"
        entities = self.analyzer.extract_entities(content)
        self.assertIsInstance(entities, list)
        self.assertTrue(len(entities) > 0)
    
    def test_calculate_suggestion_confidence(self):
        content = "Please add a new feature to improve user experience"
        confidence = self.analyzer.calculate_suggestion_confidence(content)
        self.assertIsInstance(confidence, float)
        self.assertTrue(0 <= confidence <= 1)
    
    def test_calculate_feedback_impact(self):
        content = "This is an urgent issue that affects many users"
        impact = self.analyzer.calculate_feedback_impact(content)
        self.assertIsInstance(impact, float)
        self.assertTrue(0 <= impact <= 1)
    
    def test_analyze_sentiment(self):
        content = "This is a great product with excellent features"
        doc = self.analyzer.nlp(content)
        sentiment = self.analyzer.analyze_sentiment(doc)
        self.assertIsInstance(sentiment, float)
        self.assertTrue(0 <= sentiment <= 1)
    
    def test_analyze_urgency(self):
        content = "This needs to be fixed immediately"
        doc = self.analyzer.nlp(content)
        urgency = self.analyzer.analyze_urgency(doc)
        self.assertIsInstance(urgency, float)
        self.assertTrue(0 <= urgency <= 1)
    
    def test_analyze_scope(self):
        content = "The issue affects users in New York and London"
        doc = self.analyzer.nlp(content)
        scope = self.analyzer.analyze_scope(doc)
        self.assertIsInstance(scope, float)
        self.assertTrue(0 <= scope <= 1)
    
    def test_extract_action(self):
        content = "Please generate a report for sales data"
        action = self.analyzer.extract_action(content)
        self.assertIsInstance(action, str)
        self.assertTrue(len(action) > 0)
    
    def test_extract_parameters(self):
        content = "Show sales data from 2023-01-01 to 2023-12-31"
        parameters = self.analyzer.extract_parameters(content)
        self.assertIsInstance(parameters, dict)
        self.assertTrue('dates' in parameters)
    
    def test_extract_target(self):
        content = "Generate a report for sales analysis"
        target = self.analyzer.extract_target(content)
        self.assertIsInstance(target, str)
        self.assertTrue(len(target) > 0)
    
    def test_extract_dates(self):
        content = "Data from 2023-01-01 to 2023-12-31"
        dates = self.analyzer.extract_dates(content)
        self.assertIsInstance(dates, list)
        self.assertTrue(len(dates) > 0)
        self.assertIsInstance(dates[0], datetime)
    
    def test_extract_metrics(self):
        content = "Show total sales and revenue metrics"
        metrics = self.analyzer.extract_metrics(content)
        self.assertIsInstance(metrics, list)
        self.assertTrue(len(metrics) > 0)
    
    def test_extract_filters(self):
        content = "Filter by region and product category"
        filters = self.analyzer.extract_filters(content)
        self.assertIsInstance(filters, dict)
        self.assertTrue(len(filters) > 0)
    
    def test_extract_format(self):
        content = "Export data in CSV format"
        format_type = self.analyzer.extract_format(content)
        self.assertIsInstance(format_type, str)
        self.assertTrue(len(format_type) > 0)
    
    def test_analyze_content(self):
        content = "Please generate a sales report for Q1 2023 in CSV format"
        analysis = self.analyzer.analyze_content(content)
        self.assertIsInstance(analysis, dict)
        self.assertTrue(len(analysis) > 0)
        self.assertTrue('action' in analysis)
        self.assertTrue('target' in analysis)
        self.assertTrue('parameters' in analysis)
        self.assertTrue('format' in analysis)
        self.assertTrue('confidence' in analysis)
        self.assertTrue('impact' in analysis)

if __name__ == '__main__':
    unittest.main() 