from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class ReportType(Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    PERFORMANCE = "performance"
    COMPARATIVE = "comparative"
    FORECAST = "forecast"
    CUSTOM = "custom"

class AnalysisType(Enum):
    TREND = "trend"
    COMPARISON = "comparison"
    CORRELATION = "correlation"
    FORECAST = "forecast"
    BENCHMARK = "benchmark"
    CUSTOM = "custom"

@dataclass
class ReportTemplate:
    id: str
    name: str
    description: str
    type: ReportType
    parameters: Dict[str, Any]
    layout: Dict[str, Any]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Report:
    id: str
    template_id: str
    name: str
    description: str
    type: ReportType
    parameters: Dict[str, Any]
    data: Dict[str, Any]
    status: str = "draft"  # draft, generated, archived
    file_path: Optional[str]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Analysis:
    id: str
    name: str
    description: str
    type: AnalysisType
    parameters: Dict[str, Any]
    data: Dict[str, Any]
    result: Dict[str, Any]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class AnalyticsManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, ReportTemplate] = {}
        self.reports: Dict[str, Report] = {}
        self.analyses: Dict[str, Analysis] = {}
        
        # Load report templates from file
        self.load_report_templates()
    
    def load_report_templates(self):
        """Load report templates from JSON file"""
        try:
            templates_file = os.path.join(os.path.dirname(__file__), 'report_templates.json')
            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                    for template_data in templates_data:
                        template = ReportTemplate(
                            id=template_data['id'],
                            name=template_data['name'],
                            description=template_data['description'],
                            type=ReportType(template_data['type']),
                            parameters=template_data['parameters'],
                            layout=template_data['layout'],
                            created_by=template_data['created_by']
                        )
                        self.templates[template.id] = template
                self.logger.info("Report templates loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading report templates: {str(e)}")
    
    def add_template(self, template: ReportTemplate) -> bool:
        """Add report template"""
        try:
            if template.id in self.templates:
                self.logger.warning(f"Template with ID {template.id} already exists")
                return False
            
            self.templates[template.id] = template
            self.logger.info(f"Report template added: {template.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding report template: {str(e)}")
            return False
    
    def generate_report(self, report: Report) -> bool:
        """Generate report from template"""
        try:
            template = self.templates.get(report.template_id)
            if not template:
                self.logger.error(f"Template {report.template_id} not found")
                return False
            
            # Get data based on report type and parameters
            data = self.get_report_data(report.type, report.parameters)
            
            # Apply template layout
            report.data = self.apply_template_layout(template.layout, data)
            
            # Save report
            report.file_path = self.save_report(report.id, report.data)
            report.status = "generated"
            report.updated_at = datetime.now()
            
            self.logger.info(f"Report generated: {report.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return False
    
    def get_report_data(self, report_type: ReportType, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for report"""
        try:
            if report_type == ReportType.FINANCIAL:
                return self.get_financial_data(parameters)
            elif report_type == ReportType.OPERATIONAL:
                return self.get_operational_data(parameters)
            elif report_type == ReportType.PERFORMANCE:
                return self.get_performance_data(parameters)
            elif report_type == ReportType.COMPARATIVE:
                return self.get_comparative_data(parameters)
            elif report_type == ReportType.FORECAST:
                return self.get_forecast_data(parameters)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting report data: {str(e)}")
            return {}
    
    def get_financial_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial data"""
        # Implement financial data retrieval
        return {
            "summary": {
                "total_revenue": Decimal('0'),
                "total_expenses": Decimal('0'),
                "net_profit": Decimal('0')
            },
            "details": []
        }
    
    def get_operational_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get operational data"""
        # Implement operational data retrieval
        return {
            "summary": {
                "total_operations": 0,
                "success_rate": Decimal('0'),
                "efficiency": Decimal('0')
            },
            "details": []
        }
    
    def get_performance_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance data"""
        # Implement performance data retrieval
        return {
            "summary": {
                "response_time": Decimal('0'),
                "throughput": Decimal('0'),
                "resource_usage": Decimal('0')
            },
            "details": []
        }
    
    def get_comparative_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get comparative data"""
        # Implement comparative data retrieval
        return {
            "summary": {
                "current_period": Decimal('0'),
                "previous_period": Decimal('0'),
                "change": Decimal('0')
            },
            "details": []
        }
    
    def get_forecast_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get forecast data"""
        # Implement forecast data retrieval
        return {
            "summary": {
                "forecast": Decimal('0'),
                "confidence": Decimal('0'),
                "factors": []
            },
            "details": []
        }
    
    def apply_template_layout(self, layout: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply template layout to data"""
        try:
            result = {
                "layout": layout,
                "data": data,
                "visualizations": []
            }
            
            # Generate visualizations based on layout
            for viz_config in layout.get("visualizations", []):
                viz_data = self.prepare_visualization_data(viz_config, data)
                viz_result = self.generate_visualization(viz_config, viz_data)
                result["visualizations"].append(viz_result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error applying template layout: {str(e)}")
            return {}
    
    def prepare_visualization_data(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for visualization"""
        try:
            # Convert data to pandas DataFrame if needed
            df = pd.DataFrame(data.get("details", []))
            
            # Apply data transformations based on config
            if "transformations" in config:
                for transform in config["transformations"]:
                    if transform["type"] == "filter":
                        df = df[df[transform["field"]].isin(transform["values"])]
                    elif transform["type"] == "aggregate":
                        df = df.groupby(transform["group_by"])[transform["field"]].agg(transform["function"])
                    elif transform["type"] == "sort":
                        df = df.sort_values(transform["field"], ascending=transform.get("ascending", True))
            
            return {
                "data": df.to_dict(orient="records"),
                "config": config
            }
        except Exception as e:
            self.logger.error(f"Error preparing visualization data: {str(e)}")
            return {}
    
    def generate_visualization(self, config: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization"""
        try:
            viz_type = config.get("type", "line")
            df = pd.DataFrame(data["data"])
            
            # Create figure
            plt.figure(figsize=config.get("size", (10, 6)))
            
            # Generate visualization based on type
            if viz_type == "line":
                sns.lineplot(data=df, x=config["x"], y=config["y"])
            elif viz_type == "bar":
                sns.barplot(data=df, x=config["x"], y=config["y"])
            elif viz_type == "scatter":
                sns.scatterplot(data=df, x=config["x"], y=config["y"])
            elif viz_type == "pie":
                plt.pie(df[config["values"]], labels=df[config["labels"]])
            elif viz_type == "heatmap":
                sns.heatmap(df.pivot_table(index=config["index"], 
                                         columns=config["columns"], 
                                         values=config["values"]))
            
            # Customize plot
            plt.title(config.get("title", ""))
            plt.xlabel(config.get("xlabel", ""))
            plt.ylabel(config.get("ylabel", ""))
            
            # Save plot
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'viz_{config["id"]}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "id": config["id"],
                "type": viz_type,
                "file_path": file_path,
                "config": config
            }
        except Exception as e:
            self.logger.error(f"Error generating visualization: {str(e)}")
            return {}
    
    def save_report(self, report_id: str, data: Dict[str, Any]) -> str:
        """Save report to file"""
        try:
            # Create reports directory if not exists
            reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Save report file
            file_path = os.path.join(reports_dir, f'report_{report_id}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            return ""
    
    def perform_analysis(self, analysis: Analysis) -> bool:
        """Perform data analysis"""
        try:
            # Get data based on analysis type and parameters
            data = self.get_analysis_data(analysis.type, analysis.parameters)
            
            # Perform analysis
            result = self.execute_analysis(analysis.type, data)
            
            # Update analysis
            analysis.data = data
            analysis.result = result
            analysis.updated_at = datetime.now()
            
            self.logger.info(f"Analysis completed: {analysis.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error performing analysis: {str(e)}")
            return False
    
    def get_analysis_data(self, analysis_type: AnalysisType, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for analysis"""
        try:
            if analysis_type == AnalysisType.TREND:
                return self.get_trend_data(parameters)
            elif analysis_type == AnalysisType.COMPARISON:
                return self.get_comparison_data(parameters)
            elif analysis_type == AnalysisType.CORRELATION:
                return self.get_correlation_data(parameters)
            elif analysis_type == AnalysisType.FORECAST:
                return self.get_forecast_data(parameters)
            elif analysis_type == AnalysisType.BENCHMARK:
                return self.get_benchmark_data(parameters)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting analysis data: {str(e)}")
            return {}
    
    def execute_analysis(self, analysis_type: AnalysisType, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis"""
        try:
            if analysis_type == AnalysisType.TREND:
                return self.analyze_trend(data)
            elif analysis_type == AnalysisType.COMPARISON:
                return self.analyze_comparison(data)
            elif analysis_type == AnalysisType.CORRELATION:
                return self.analyze_correlation(data)
            elif analysis_type == AnalysisType.FORECAST:
                return self.analyze_forecast(data)
            elif analysis_type == AnalysisType.BENCHMARK:
                return self.analyze_benchmark(data)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error executing analysis: {str(e)}")
            return {}
    
    def analyze_trend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trend in data"""
        try:
            df = pd.DataFrame(data["details"])
            
            # Calculate trend statistics
            trend_stats = {
                "slope": float(stats.linregress(range(len(df)), df["value"])[0]),
                "r_squared": float(stats.linregress(range(len(df)), df["value"])[2]),
                "p_value": float(stats.linregress(range(len(df)), df["value"])[3])
            }
            
            # Generate trend visualization
            plt.figure(figsize=(10, 6))
            sns.lineplot(data=df, x="date", y="value")
            plt.title("Trend Analysis")
            
            # Save visualization
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'trend_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "statistics": trend_stats,
                "visualization": file_path,
                "interpretation": self.interpret_trend(trend_stats)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {str(e)}")
            return {}
    
    def analyze_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comparison between groups"""
        try:
            df = pd.DataFrame(data["details"])
            
            # Calculate comparison statistics
            comparison_stats = {
                "mean_difference": float(df.groupby("group")["value"].mean().diff().iloc[-1]),
                "t_statistic": float(stats.ttest_ind(df[df["group"] == "A"]["value"],
                                                   df[df["group"] == "B"]["value"])[0]),
                "p_value": float(stats.ttest_ind(df[df["group"] == "A"]["value"],
                                               df[df["group"] == "B"]["value"])[1])
            }
            
            # Generate comparison visualization
            plt.figure(figsize=(10, 6))
            sns.boxplot(data=df, x="group", y="value")
            plt.title("Comparison Analysis")
            
            # Save visualization
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'comparison_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "statistics": comparison_stats,
                "visualization": file_path,
                "interpretation": self.interpret_comparison(comparison_stats)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing comparison: {str(e)}")
            return {}
    
    def analyze_correlation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between variables"""
        try:
            df = pd.DataFrame(data["details"])
            
            # Calculate correlation statistics
            correlation_matrix = df.corr()
            correlation_stats = {
                "matrix": correlation_matrix.to_dict(),
                "significant_correlations": self.find_significant_correlations(correlation_matrix)
            }
            
            # Generate correlation visualization
            plt.figure(figsize=(10, 6))
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
            plt.title("Correlation Analysis")
            
            # Save visualization
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'correlation_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "statistics": correlation_stats,
                "visualization": file_path,
                "interpretation": self.interpret_correlation(correlation_stats)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing correlation: {str(e)}")
            return {}
    
    def analyze_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze forecast"""
        try:
            df = pd.DataFrame(data["details"])
            
            # Prepare data for forecasting
            X = np.array(range(len(df))).reshape(-1, 1)
            y = df["value"].values
            
            # Fit linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate forecast
            future_dates = np.array(range(len(df), len(df) + 12)).reshape(-1, 1)
            forecast = model.predict(future_dates)
            
            # Calculate confidence intervals
            confidence_intervals = self.calculate_confidence_intervals(model, X, y, future_dates)
            
            # Generate forecast visualization
            plt.figure(figsize=(10, 6))
            plt.plot(X, y, label="Historical")
            plt.plot(future_dates, forecast, label="Forecast")
            plt.fill_between(future_dates.ravel(),
                           confidence_intervals["lower"],
                           confidence_intervals["upper"],
                           alpha=0.2)
            plt.title("Forecast Analysis")
            plt.legend()
            
            # Save visualization
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'forecast_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "forecast": forecast.tolist(),
                "confidence_intervals": confidence_intervals,
                "model_metrics": {
                    "r_squared": float(model.score(X, y)),
                    "coefficients": model.coef_.tolist(),
                    "intercept": float(model.intercept_)
                },
                "visualization": file_path,
                "interpretation": self.interpret_forecast(model, forecast, confidence_intervals)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing forecast: {str(e)}")
            return {}
    
    def analyze_benchmark(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark performance"""
        try:
            df = pd.DataFrame(data["details"])
            
            # Calculate benchmark statistics
            benchmark_stats = {
                "mean": float(df["value"].mean()),
                "std": float(df["value"].std()),
                "percentiles": df["value"].quantile([0.25, 0.5, 0.75]).to_dict(),
                "z_scores": stats.zscore(df["value"]).tolist()
            }
            
            # Generate benchmark visualization
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x="value", kde=True)
            plt.axvline(benchmark_stats["mean"], color="r", linestyle="--", label="Mean")
            plt.title("Benchmark Analysis")
            plt.legend()
            
            # Save visualization
            viz_dir = os.path.join(os.path.dirname(__file__), 'visualizations')
            if not os.path.exists(viz_dir):
                os.makedirs(viz_dir)
            
            file_path = os.path.join(viz_dir, f'benchmark_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
            plt.savefig(file_path)
            plt.close()
            
            return {
                "statistics": benchmark_stats,
                "visualization": file_path,
                "interpretation": self.interpret_benchmark(benchmark_stats)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing benchmark: {str(e)}")
            return {}
    
    def calculate_confidence_intervals(self, model, X, y, future_dates):
        """Calculate confidence intervals for forecast"""
        try:
            # Calculate prediction standard error
            n = len(X)
            mse = np.sum((y - model.predict(X)) ** 2) / (n - 2)
            std_err = np.sqrt(mse * (1/n + (future_dates - np.mean(X))**2 / np.sum((X - np.mean(X))**2)))
            
            # Calculate confidence intervals
            t_value = stats.t.ppf(0.95, n - 2)
            lower = model.predict(future_dates) - t_value * std_err
            upper = model.predict(future_dates) + t_value * std_err
            
            return {
                "lower": lower.tolist(),
                "upper": upper.tolist()
            }
        except Exception as e:
            self.logger.error(f"Error calculating confidence intervals: {str(e)}")
            return {"lower": [], "upper": []}
    
    def find_significant_correlations(self, correlation_matrix):
        """Find significant correlations in matrix"""
        try:
            significant = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i + 1, len(correlation_matrix.columns)):
                    if abs(correlation_matrix.iloc[i, j]) > 0.7:  # Strong correlation threshold
                        significant.append({
                            "variable1": correlation_matrix.columns[i],
                            "variable2": correlation_matrix.columns[j],
                            "correlation": float(correlation_matrix.iloc[i, j])
                        })
            return significant
        except Exception as e:
            self.logger.error(f"Error finding significant correlations: {str(e)}")
            return []
    
    def interpret_trend(self, stats: Dict[str, Any]) -> str:
        """Interpret trend analysis results"""
        try:
            if stats["p_value"] < 0.05:
                if stats["slope"] > 0:
                    return "Significant upward trend"
                else:
                    return "Significant downward trend"
            else:
                return "No significant trend"
        except Exception as e:
            self.logger.error(f"Error interpreting trend: {str(e)}")
            return "Unable to interpret trend"
    
    def interpret_comparison(self, stats: Dict[str, Any]) -> str:
        """Interpret comparison analysis results"""
        try:
            if stats["p_value"] < 0.05:
                if stats["mean_difference"] > 0:
                    return "Significant difference: Group B is higher"
                else:
                    return "Significant difference: Group A is higher"
            else:
                return "No significant difference between groups"
        except Exception as e:
            self.logger.error(f"Error interpreting comparison: {str(e)}")
            return "Unable to interpret comparison"
    
    def interpret_correlation(self, stats: Dict[str, Any]) -> str:
        """Interpret correlation analysis results"""
        try:
            significant = stats["significant_correlations"]
            if significant:
                return f"Found {len(significant)} strong correlations"
            else:
                return "No strong correlations found"
        except Exception as e:
            self.logger.error(f"Error interpreting correlation: {str(e)}")
            return "Unable to interpret correlation"
    
    def interpret_forecast(self, model, forecast, confidence_intervals) -> str:
        """Interpret forecast analysis results"""
        try:
            trend = "increasing" if model.coef_[0] > 0 else "decreasing"
            confidence = "high" if model.score(X, y) > 0.7 else "moderate" if model.score(X, y) > 0.4 else "low"
            return f"Forecast shows {trend} trend with {confidence} confidence"
        except Exception as e:
            self.logger.error(f"Error interpreting forecast: {str(e)}")
            return "Unable to interpret forecast"
    
    def interpret_benchmark(self, stats: Dict[str, Any]) -> str:
        """Interpret benchmark analysis results"""
        try:
            if stats["std"] < stats["mean"] * 0.1:
                return "Consistent performance"
            else:
                return "Variable performance"
        except Exception as e:
            self.logger.error(f"Error interpreting benchmark: {str(e)}")
            return "Unable to interpret benchmark" 