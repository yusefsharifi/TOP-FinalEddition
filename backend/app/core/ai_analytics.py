from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
import json
import os
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import joblib

class AnalysisType(Enum):
    SALES = "sales"
    INVENTORY = "inventory"
    FINANCE = "finance"
    CUSTOMER = "customer"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    HR = "hr"
    COMPLIANCE = "compliance"

class RecommendationType(Enum):
    PRODUCT = "product"
    PRICE = "price"
    INVENTORY = "inventory"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    CUSTOMER = "customer"
    FINANCE = "finance"
    HR = "hr"

@dataclass
class BusinessMetric:
    id: str
    type: AnalysisType
    name: str
    value: Decimal
    unit: str
    timestamp: datetime
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AIRecommendation:
    id: str
    type: RecommendationType
    title: str
    description: str
    priority: int
    impact_score: Decimal
    implementation_cost: Decimal
    expected_roi: Decimal
    target_systems: List[AnalysisType]
    supporting_data: Dict[str, Any]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PredictiveModel:
    id: str
    name: str
    type: str
    target_metric: str
    features: List[str]
    accuracy: Decimal
    last_trained: datetime
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class BusinessAIAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, BusinessMetric] = {}
        self.recommendations: Dict[str, AIRecommendation] = {}
        self.models: Dict[str, PredictiveModel] = {}
        
        # Initialize ML models
        self.customer_clustering_model = KMeans(n_clusters=5, random_state=42)
        self.sales_prediction_model = RandomForestRegressor(random_state=42)
        self.customer_churn_model = RandomForestClassifier(random_state=42)
        self.demand_forecast_model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(30, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        self.scaler = StandardScaler()
        
        # Create necessary directories
        self.create_directories()
        
        # Load saved models if available
        self.load_models()
    
    def create_directories(self):
        """Create necessary directories for AI analytics"""
        try:
            # Create AI data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'ai_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create AI models directory
            models_dir = os.path.join(os.path.dirname(__file__), 'ai_models')
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            
            # Create AI reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'ai_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("AI analytics directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_models(self):
        """Load saved ML models"""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), 'ai_models')
            
            # Load customer clustering model
            clustering_path = os.path.join(models_dir, 'customer_clustering.joblib')
            if os.path.exists(clustering_path):
                self.customer_clustering_model = joblib.load(clustering_path)
            
            # Load sales prediction model
            sales_path = os.path.join(models_dir, 'sales_prediction.joblib')
            if os.path.exists(sales_path):
                self.sales_prediction_model = joblib.load(sales_path)
            
            # Load customer churn model
            churn_path = os.path.join(models_dir, 'customer_churn.joblib')
            if os.path.exists(churn_path):
                self.customer_churn_model = joblib.load(churn_path)
            
            # Load demand forecast model
            demand_path = os.path.join(models_dir, 'demand_forecast.h5')
            if os.path.exists(demand_path):
                self.demand_forecast_model.load_weights(demand_path)
            
            self.logger.info("ML models loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
    
    def save_models(self):
        """Save trained ML models"""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), 'ai_models')
            
            # Save customer clustering model
            joblib.dump(self.customer_clustering_model, os.path.join(models_dir, 'customer_clustering.joblib'))
            
            # Save sales prediction model
            joblib.dump(self.sales_prediction_model, os.path.join(models_dir, 'sales_prediction.joblib'))
            
            # Save customer churn model
            joblib.dump(self.customer_churn_model, os.path.join(models_dir, 'customer_churn.joblib'))
            
            # Save demand forecast model
            self.demand_forecast_model.save_weights(os.path.join(models_dir, 'demand_forecast.h5'))
            
            self.logger.info("ML models saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving models: {str(e)}")
    
    def analyze_sales_data(self, sales_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales data and generate insights"""
        try:
            # Convert sales data to DataFrame
            df = pd.DataFrame(sales_data)
            
            # Analyze sales trends
            sales_trends = {
                'daily': df.groupby(df['date'].dt.date)['amount'].sum().to_dict(),
                'weekly': df.groupby(df['date'].dt.isocalendar().week)['amount'].sum().to_dict(),
                'monthly': df.groupby(df['date'].dt.month)['amount'].sum().to_dict()
            }
            
            # Analyze product performance
            product_performance = df.groupby('product_id').agg({
                'quantity': 'sum',
                'amount': 'sum',
                'order_id': 'count'
            }).to_dict()
            
            # Analyze customer segments
            customer_segments = df.groupby('customer_id').agg({
                'amount': 'sum',
                'order_id': 'count'
            }).to_dict()
            
            # Generate recommendations
            recommendations = self.generate_sales_recommendations(sales_trends, product_performance, customer_segments)
            
            return {
                'trends': sales_trends,
                'product_performance': product_performance,
                'customer_segments': customer_segments,
                'recommendations': recommendations
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sales data: {str(e)}")
            return {}
    
    def analyze_inventory_data(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inventory data and generate insights"""
        try:
            # Convert inventory data to DataFrame
            df = pd.DataFrame(inventory_data)
            
            # Analyze stock levels
            stock_levels = df.groupby('product_id').agg({
                'quantity': 'sum',
                'value': 'sum'
            }).to_dict()
            
            # Analyze turnover rates
            turnover_rates = df.groupby('product_id').agg({
                'quantity': lambda x: x.sum() / x.mean() if x.mean() != 0 else 0
            }).to_dict()
            
            # Analyze stockouts
            stockouts = df[df['quantity'] == 0].groupby('product_id').size().to_dict()
            
            # Generate recommendations
            recommendations = self.generate_inventory_recommendations(stock_levels, turnover_rates, stockouts)
            
            return {
                'stock_levels': stock_levels,
                'turnover_rates': turnover_rates,
                'stockouts': stockouts,
                'recommendations': recommendations
            }
        except Exception as e:
            self.logger.error(f"Error analyzing inventory data: {str(e)}")
            return {}
    
    def analyze_financial_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial data and generate insights"""
        try:
            # Convert financial data to DataFrame
            df = pd.DataFrame(financial_data)
            
            # Analyze revenue trends
            revenue_trends = df.groupby(df['date'].dt.date)['revenue'].sum().to_dict()
            
            # Analyze costs
            cost_analysis = df.groupby('cost_type').agg({
                'amount': 'sum'
            }).to_dict()
            
            # Analyze profitability
            profitability = df.groupby('product_id').agg({
                'revenue': 'sum',
                'cost': 'sum',
                'profit': 'sum'
            }).to_dict()
            
            # Generate recommendations
            recommendations = self.generate_financial_recommendations(revenue_trends, cost_analysis, profitability)
            
            return {
                'revenue_trends': revenue_trends,
                'cost_analysis': cost_analysis,
                'profitability': profitability,
                'recommendations': recommendations
            }
        except Exception as e:
            self.logger.error(f"Error analyzing financial data: {str(e)}")
            return {}
    
    def analyze_customer_data(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer data and generate insights"""
        try:
            # Convert customer data to DataFrame
            df = pd.DataFrame(customer_data)
            
            # Prepare features for clustering
            features = ['total_orders', 'total_amount', 'average_order_value', 'payment_performance', 'return_rate']
            X = self.scaler.fit_transform(df[features])
            
            # Perform customer clustering
            clusters = self.customer_clustering_model.fit_predict(X)
            
            # Analyze customer segments
            customer_segments = {}
            for i in range(5):
                segment_data = df[clusters == i]
                customer_segments[f"segment_{i}"] = {
                    'size': len(segment_data),
                    'characteristics': segment_data[features].mean().to_dict()
                }
            
            # Predict customer churn
            churn_probabilities = self.customer_churn_model.predict_proba(X)
            
            # Generate recommendations
            recommendations = self.generate_customer_recommendations(customer_segments, churn_probabilities)
            
            return {
                'segments': customer_segments,
                'churn_probabilities': churn_probabilities.tolist(),
                'recommendations': recommendations
            }
        except Exception as e:
            self.logger.error(f"Error analyzing customer data: {str(e)}")
            return {}
    
    def generate_sales_recommendations(self, trends: Dict[str, Any], product_performance: Dict[str, Any], customer_segments: Dict[str, Any]) -> List[AIRecommendation]:
        """Generate sales-related recommendations"""
        recommendations = []
        
        # Analyze sales trends
        if trends['monthly']:
            last_month = max(trends['monthly'].keys())
            if trends['monthly'][last_month] < sum(trends['monthly'].values()) / len(trends['monthly']):
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.SALES,
                    title="Sales Decline Alert",
                    description="Monthly sales have declined below average. Consider implementing promotional activities.",
                    priority=1,
                    impact_score=Decimal('0.8'),
                    implementation_cost=Decimal('1000'),
                    expected_roi=Decimal('3.5'),
                    target_systems=[AnalysisType.SALES, AnalysisType.MARKETING],
                    supporting_data={'trends': trends},
                    created_by="system"
                ))
        
        # Analyze product performance
        for product_id, performance in product_performance.items():
            if performance['quantity'] < 100:
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.PRODUCT,
                    title=f"Low Performance Product: {product_id}",
                    description="Product shows low sales volume. Consider reviewing pricing or marketing strategy.",
                    priority=2,
                    impact_score=Decimal('0.6'),
                    implementation_cost=Decimal('500'),
                    expected_roi=Decimal('2.0'),
                    target_systems=[AnalysisType.SALES, AnalysisType.MARKETING],
                    supporting_data={'performance': performance},
                    created_by="system"
                ))
        
        return recommendations
    
    def generate_inventory_recommendations(self, stock_levels: Dict[str, Any], turnover_rates: Dict[str, Any], stockouts: Dict[str, Any]) -> List[AIRecommendation]:
        """Generate inventory-related recommendations"""
        recommendations = []
        
        # Analyze stock levels
        for product_id, levels in stock_levels.items():
            if levels['quantity'] < 100:
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.INVENTORY,
                    title=f"Low Stock Alert: {product_id}",
                    description="Product stock level is below threshold. Consider reordering.",
                    priority=1,
                    impact_score=Decimal('0.9'),
                    implementation_cost=Decimal('2000'),
                    expected_roi=Decimal('4.0'),
                    target_systems=[AnalysisType.INVENTORY],
                    supporting_data={'stock_levels': levels},
                    created_by="system"
                ))
        
        # Analyze turnover rates
        for product_id, rate in turnover_rates.items():
            if rate < 2:
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.INVENTORY,
                    title=f"Slow Moving Inventory: {product_id}",
                    description="Product has low turnover rate. Consider promotional activities or price adjustments.",
                    priority=2,
                    impact_score=Decimal('0.7'),
                    implementation_cost=Decimal('1000'),
                    expected_roi=Decimal('2.5'),
                    target_systems=[AnalysisType.INVENTORY, AnalysisType.MARKETING],
                    supporting_data={'turnover_rate': rate},
                    created_by="system"
                ))
        
        return recommendations
    
    def generate_financial_recommendations(self, revenue_trends: Dict[str, Any], cost_analysis: Dict[str, Any], profitability: Dict[str, Any]) -> List[AIRecommendation]:
        """Generate financial-related recommendations"""
        recommendations = []
        
        # Analyze revenue trends
        if revenue_trends:
            last_month = max(revenue_trends.keys())
            if revenue_trends[last_month] < sum(revenue_trends.values()) / len(revenue_trends):
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.FINANCE,
                    title="Revenue Decline Alert",
                    description="Monthly revenue has declined below average. Review pricing and cost structure.",
                    priority=1,
                    impact_score=Decimal('0.9'),
                    implementation_cost=Decimal('5000'),
                    expected_roi=Decimal('4.0'),
                    target_systems=[AnalysisType.FINANCE],
                    supporting_data={'revenue_trends': revenue_trends},
                    created_by="system"
                ))
        
        # Analyze costs
        for cost_type, amount in cost_analysis.items():
            if amount > sum(cost_analysis.values()) / len(cost_analysis) * 1.5:
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.FINANCE,
                    title=f"High Cost Alert: {cost_type}",
                    description=f"Cost type shows significant increase. Review and optimize {cost_type} expenses.",
                    priority=2,
                    impact_score=Decimal('0.8'),
                    implementation_cost=Decimal('3000'),
                    expected_roi=Decimal('3.0'),
                    target_systems=[AnalysisType.FINANCE],
                    supporting_data={'cost_analysis': {cost_type: amount}},
                    created_by="system"
                ))
        
        return recommendations
    
    def generate_customer_recommendations(self, segments: Dict[str, Any], churn_probabilities: np.ndarray) -> List[AIRecommendation]:
        """Generate customer-related recommendations"""
        recommendations = []
        
        # Analyze customer segments
        for segment_id, segment_data in segments.items():
            if segment_data['size'] < 100:
                recommendations.append(AIRecommendation(
                    id=str(uuid.uuid4()),
                    type=RecommendationType.CUSTOMER,
                    title=f"Small Customer Segment: {segment_id}",
                    description="Segment size is below target. Consider targeted marketing campaigns.",
                    priority=2,
                    impact_score=Decimal('0.6'),
                    implementation_cost=Decimal('2000'),
                    expected_roi=Decimal('2.5'),
                    target_systems=[AnalysisType.CUSTOMER, AnalysisType.MARKETING],
                    supporting_data={'segment_data': segment_data},
                    created_by="system"
                ))
        
        # Analyze churn risk
        high_risk_customers = np.where(churn_probabilities[:, 1] > 0.7)[0]
        if len(high_risk_customers) > 0:
            recommendations.append(AIRecommendation(
                id=str(uuid.uuid4()),
                type=RecommendationType.CUSTOMER,
                title="High Customer Churn Risk",
                description=f"Found {len(high_risk_customers)} customers with high churn risk. Implement retention strategies.",
                priority=1,
                impact_score=Decimal('0.9'),
                implementation_cost=Decimal('3000'),
                expected_roi=Decimal('4.0'),
                target_systems=[AnalysisType.CUSTOMER],
                supporting_data={'high_risk_count': len(high_risk_customers)},
                created_by="system"
            ))
        
        return recommendations
    
    def generate_comprehensive_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate comprehensive business analysis report"""
        try:
            # Collect data from all systems
            sales_data = self.collect_sales_data(start_date, end_date)
            inventory_data = self.collect_inventory_data(start_date, end_date)
            financial_data = self.collect_financial_data(start_date, end_date)
            customer_data = self.collect_customer_data(start_date, end_date)
            
            # Analyze data from each system
            sales_analysis = self.analyze_sales_data(sales_data)
            inventory_analysis = self.analyze_inventory_data(inventory_data)
            financial_analysis = self.analyze_financial_data(financial_data)
            customer_analysis = self.analyze_customer_data(customer_data)
            
            # Generate recommendations
            recommendations = (
                sales_analysis.get('recommendations', []) +
                inventory_analysis.get('recommendations', []) +
                financial_analysis.get('recommendations', []) +
                customer_analysis.get('recommendations', [])
            )
            
            # Sort recommendations by priority and impact
            recommendations.sort(key=lambda x: (x.priority, x.impact_score), reverse=True)
            
            # Generate report
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "sales_analysis": sales_analysis,
                "inventory_analysis": inventory_analysis,
                "financial_analysis": financial_analysis,
                "customer_analysis": customer_analysis,
                "recommendations": {
                    "total": len(recommendations),
                    "by_priority": {
                        "high": len([r for r in recommendations if r.priority == 1]),
                        "medium": len([r for r in recommendations if r.priority == 2]),
                        "low": len([r for r in recommendations if r.priority == 3])
                    },
                    "by_type": {
                        "sales": len([r for r in recommendations if r.type == RecommendationType.SALES]),
                        "inventory": len([r for r in recommendations if r.type == RecommendationType.INVENTORY]),
                        "finance": len([r for r in recommendations if r.type == RecommendationType.FINANCE]),
                        "customer": len([r for r in recommendations if r.type == RecommendationType.CUSTOMER])
                    },
                    "details": [
                        {
                            "id": r.id,
                            "type": r.type.value,
                            "title": r.title,
                            "priority": r.priority,
                            "impact_score": str(r.impact_score),
                            "implementation_cost": str(r.implementation_cost),
                            "expected_roi": str(r.expected_roi),
                            "target_systems": [s.value for s in r.target_systems]
                        }
                        for r in recommendations
                    ]
                }
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {str(e)}")
            return {}
    
    def collect_sales_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Collect sales data from the sales system"""
        # This method should be implemented to collect data from the sales system
        return {}
    
    def collect_inventory_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Collect inventory data from the inventory system"""
        # This method should be implemented to collect data from the inventory system
        return {}
    
    def collect_financial_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Collect financial data from the financial system"""
        # This method should be implemented to collect data from the financial system
        return {}
    
    def collect_customer_data(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Collect customer data from the customer management system"""
        # This method should be implemented to collect data from the customer management system
        return {} 