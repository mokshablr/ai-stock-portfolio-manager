import os
import json
import schedule
import time
from datetime import datetime, timedelta
from data_collector import DataCollector
from llm_connector import LLMConnector, DecisionEngine
from portfolio_analyzer import PortfolioAnalyzer
from news_aggregator import NewsAggregator
from report_generator import ReportGenerator

class PortfolioAIWorkflow:
    def __init__(self, portfolio_file="portfolio.json"):
        """Initialize the full workflow"""
        # Create necessary directories
        self.base_dir = "portfolio_ai"
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Initialize components
        self.data_collector = DataCollector(portfolio_file)
        self.llm = LLMConnector()
        self.portfolio_analyzer = PortfolioAnalyzer(self.data_collector)
        self.news_aggregator = NewsAggregator(self.data_collector, self.llm)
        self.decision_engine = DecisionEngine(self.portfolio_analyzer, self.news_aggregator, self.llm)
        self.report_generator = ReportGenerator(self.portfolio_analyzer, self.news_aggregator, self.decision_engine)
        
        # Status tracking
        self.last_run = None
        self.run_history = []
    
    def run_daily_workflow(self):
        """Run the complete daily workflow"""
        start_time = datetime.now()
        print(f"Starting daily workflow at {start_time}")
        
        try:
            # 1. Collect data
            print("1 - Collecting data...")
            print("1.1 - Collecting stock data...")
            stock_data = self.data_collector.fetch_stock_data("1y")
            print("1.1 - Collected stock data successfully")
            print("1.2 - Collecting news...")
            news = self.data_collector.fetch_news(days=3)
            print("1.2 - Collected news successfully")
            print("1 - Data collection completed successfully")
            
            # 2. Run portfolio analysis
            print("2 - Running portfolio analysis...")
            print("2.1 - Analyzing portfolio...")
            performance = self.portfolio_analyzer.calculate_portfolio_performance(stock_data=stock_data)
            print("2.1 - Portfolio performance calculated successfully")
            print("2.2 - Analyzing stock contributions...")
            contributions = self.portfolio_analyzer.analyze_stock_contributions(stock_data=stock_data)
            print("2.2 Stock contributions analyzed successfully")
            print("2.3 - Generating optimization suggestions...")
            suggestions = self.portfolio_analyzer.generate_optimization_suggestions(performance, contributions, stock_data=stock_data)
            print("2.3 Optimization suggestions generated successfully")
            print("2 - Portfolio analysis completed successfully")

            # 3. Process news
            print("3 - Processing news...")
            print("3.1 - Processing news...")
            categorized_news = self.news_aggregator.fetch_and_categorize_news(news_items=news)
            print("3.1 - News categorized successfully")
            print("3.2 - Summarizing news...")
            news_summary = self.news_aggregator.summarize_news(categorized_news)
            print("3.2 - News summarized successfully")
            print("3 - News processing completed successfully")

            # 4. Generate decisions
            print("4 - Generating investment decisions...")
            print("4.1 - Generating investment decisions...")
            decisions = self.decision_engine.generate_portfolio_decisions(performance, contributions, suggestions, news_summary)
            print("4.1 - Investment decisions generated successfully")
            print("4 - Investment decisions completed successfully")

            # 5. Create reports
            print("5 - Generating reports...")
            print("5.1 - Generating performance report...")
            report_info = self.report_generator.generate_daily_report(performance, contributions, suggestions, news_summary, decisions)
            print("5.1 - Performance report generated successfully")
            print("5 - Report generation completed successfully")

            # 6. Log completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_log = {
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration,
                "status": "success",
                "report_path": report_info["report_path"],
                "summary_path": report_info["summary_path"]
            }
            
            self.last_run = run_log
            self.run_history.append(run_log)
            
            # Save run history
            with open(os.path.join(self.base_dir, "run_history.json"), "w", encoding="utf-8") as f:
                json.dump(self.run_history, f, indent=2)
            
            print(f"Workflow completed successfully in {duration:.2f} seconds")
            print(f"Reports saved to: {report_info['report_path']}")
            
            # Return summary for potential notification
            return report_info["text_summary"]
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_log = {
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": duration,
                "status": "error",
                "error": str(e)
            }
            
            self.last_run = error_log
            self.run_history.append(error_log)
            
            # Save run history
            with open(os.path.join(self.base_dir, "run_history.json"), "w", encoding="utf-8") as f:
                json.dump(self.run_history, f, indent=2)
            
            print(f"Workflow failed: {str(e)}")
            return f"ERROR: Portfolio AI workflow failed: {str(e)}"
    
    def schedule_daily_run(self, time_str="18:00"):
        """Schedule daily run at specific time"""
        schedule.every().day.at(time_str).do(self.run_daily_workflow)
        print(f"Scheduled daily workflow to run at {time_str}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_on_demand(self):
        """Run workflow immediately on demand"""
        return self.run_daily_workflow()
