import os
from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import base64
from io import BytesIO

class ReportGenerator:
    def __init__(self, portfolio_analyzer, news_aggregator, decision_engine):
        """
        Initialize the report generator
        portfolio_analyzer: Instance of PortfolioAnalyzer
        news_aggregator: Instance of NewsAggregator
        decision_engine: Instance of DecisionEngine
        """
        self.analyzer = portfolio_analyzer
        self.news = news_aggregator
        self.decisions = decision_engine
        self.reports_dir = "generated_reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_daily_report(self):
        """Generate a comprehensive daily report"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 1. Get all necessary data
        performance_df, metrics = self.analyzer.calculate_portfolio_performance()
        contributions = self.analyzer.analyze_stock_contributions()
        suggestions = self.analyzer.generate_optimization_suggestions()
        news_summary = self.news.summarize_news()
        decision_report = self.decisions.generate_portfolio_decisions()
        
        # 2. Create visualizations
        self.analyzer.visualize_portfolio()
        
        # 3. Create PDF report
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, f"Portfolio Report - {today}", 0, 1, "C")
        
        # Performance metrics
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Portfolio Performance", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(190, 5, f"Total Return: {metrics['total_return']:.2%}")
        pdf.multi_cell(190, 5, f"Annualized Return: {metrics['annualized_return']:.2%}")
        pdf.multi_cell(190, 5, f"Volatility: {metrics['volatility']:.2%}")
        pdf.multi_cell(190, 5, f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        pdf.multi_cell(190, 5, f"Maximum Drawdown: {metrics['max_drawdown']:.2%}")
        
        # Add portfolio composition image
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Portfolio Composition", 0, 1, "L")
        composition_path = os.path.join(self.analyzer.results_dir, "portfolio_composition.png")
        if os.path.exists(composition_path):
            pdf.image(composition_path, x=10, y=30, w=170)
        
        # Performance chart
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Performance Chart", 0, 1, "L")
        performance_path = os.path.join(self.analyzer.results_dir, "portfolio_performance.png")
        if os.path.exists(performance_path):
            pdf.image(performance_path, x=10, y=30, w=170)
        
        # Stock returns
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Individual Stock Returns", 0, 1, "L")
        returns_path = os.path.join(self.analyzer.results_dir, "stock_returns.png")
        if os.path.exists(returns_path):
            pdf.image(returns_path, x=10, y=30, w=170)
        
        # Optimization suggestions
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Optimization Suggestions", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        for suggestion in suggestions:
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(190, 5, f"{suggestion['type']} - {suggestion['symbol']} ({suggestion['severity']})")
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(190, 5, f"Action: {suggestion['action']}")
            pdf.multi_cell(190, 5, f"Reasoning: {suggestion['reasoning']}")
            pdf.ln(5)
        
        # News summary
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "News Summary", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        # Split by sections to handle formatting
        news_sections = news_summary.split("\n\n")
        for section in news_sections:
            if section.strip():
                if section.startswith("Key Takeaways") or section.startswith("Potential Impact") or section.startswith("Stocks to Watch"):
                    pdf.set_font("Arial", "B", 12)
                    pdf.multi_cell(190, 5, section.split("\n")[0])
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(190, 5, "\n".join(section.split("\n")[1:]))
                else:
                    pdf.multi_cell(190, 5, section)
                pdf.ln(3)
        
        # Decision report
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "Portfolio Decisions & Recommendations", 0, 1, "L")
        pdf.set_font("Arial", "", 10)
        # Split by sections
        decision_sections = decision_report.split("\n\n")
        for section in decision_sections:
            if section.strip():
                if any(section.startswith(heading) for heading in ["PORTFOLIO ASSESSMENT", "ACTIONABLE RECOMMENDATIONS", "MARKET OUTLOOK"]):
                    pdf.set_font("Arial", "B", 12)
                    pdf.multi_cell(190, 5, section.split("\n")[0])
                    pdf.set_font("Arial", "", 10)
                    pdf.multi_cell(190, 5, "\n".join(section.split("\n")[1:]))
                else:
                    pdf.multi_cell(190, 5, section)
                pdf.ln(3)
        
        # Save PDF
        report_path = os.path.join(self.reports_dir, f"portfolio_report_{today}.pdf")
        pdf.output(report_path)
        
        news_snippet = news_summary.split('\n\n')[0] if '\n\n' in news_summary else news_summary[:200]
        top_reco = decision_report.split('\n\n')[1] if '\n\n' in decision_report else decision_report[:200]
        
        # Also create a simple text summary for email/messaging
        text_summary = f"""
        PORTFOLIO REPORT SUMMARY - {today}
        
        Performance: {metrics['total_return']:.2%} total return, Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
        
        Key Suggestions:
        {", ".join([f"{s['symbol']} ({s['action']})" for s in suggestions[:3]])}
        
        News Impact:
        {news_snippet}
        
        Top Recommendation:
        {top_reco}
        
        Full report available at: {report_path}
        """
        
        summary_path = os.path.join(self.reports_dir, f"summary_{today}.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(text_summary)
        
        return {
            "report_path": report_path,
            "summary_path": summary_path,
            "text_summary": text_summary
        }
