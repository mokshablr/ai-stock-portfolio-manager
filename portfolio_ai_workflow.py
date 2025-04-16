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
            print("Collecting stock data...")
            stock_data = self.data_collector.fetch_stock_data()
            print("Collected stock data successfully")
            
            print("Collecting news...")
            news = self.data_collector.fetch_news()
            print("Collected news successfully")
            
            # 2. Run portfolio analysis
            print("Analyzing portfolio...")
            performance = self.portfolio_analyzer.calculate_portfolio_performance()
            contributions = self.portfolio_analyzer.analyze_stock_contributions()
            suggestions = self.portfolio_analyzer.generate_optimization_suggestions()
            print("Portfolio analysis completed successfully")

            # 3. Process news
            print("Processing news...")
            categorized_news = self.news_aggregator.fetch_and_categorize_news()
            news_summary = self.news_aggregator.summarize_news(categorized_news)
            print("News processing completed successfully")

            # 4. Generate decisions
            print("Generating investment decisions...")
            decisions = self.decision_engine.generate_portfolio_decisions()
            print("Investment decisions generated successfully")

            # 5. Create reports
            print("Generating reports...")
            report_info = self.report_generator.generate_daily_report()
            print("Reports generated successfully")

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
