import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class LLMConnector:
    def __init__(self, endpoint=None):
        """
        Initialize the LLM connector for Ollama
        endpoint: API endpoint for Ollama
        """
        self.endpoint = endpoint or os.getenv("OLLAMA_API_ENDPOINT")
        self.model = "llama3"  # or any other model you have in Ollama
    
    def generate_content(self, prompt, max_tokens=2000):
        """
        Generate content using local LLM via Ollama
        prompt: The prompt to send to the LLM
        max_tokens: Maximum number of tokens to generate
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.endpoint, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Error: No response found")
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Exception when calling Ollama API: {str(e)}"

class DecisionEngine:
    def __init__(self, portfolio_analyzer, news_aggregator, llm_connector):
        """
        Initialize the decision engine
        portfolio_analyzer: Instance of PortfolioAnalyzer
        news_aggregator: Instance of NewsAggregator
        llm_connector: Instance of LLMConnector
        """
        self.analyzer = portfolio_analyzer
        self.news = news_aggregator
        self.llm = llm_connector
        self.decisions_dir = "decision_reports"
        os.makedirs(self.decisions_dir, exist_ok=True)
    
    def generate_portfolio_decisions(self):
        """Generate portfolio decisions based on analysis and news"""
        # 1. Get portfolio analysis data
        performance_metrics = self.analyzer.calculate_portfolio_performance()[1]
        stock_contributions = self.analyzer.analyze_stock_contributions()
        suggestions = self.analyzer.generate_optimization_suggestions()
        
        # 2. Get news summary
        news_summary = self.news.summarize_news()
        
        # 3. Create prompt for LLM
        prompt_template = """
        You are a sophisticated financial advisor specializing in the Indian stock market.
        
        I need your analysis and recommendations for my stock portfolio based on the following data:
        
        PORTFOLIO PERFORMANCE METRICS:
        {performance_metrics}
        
        OPTIMIZATION SUGGESTIONS (from quantitative analysis):
        {suggestions}
        
        RECENT NEWS SUMMARY:
        {news_summary}
        
        Based on this information, please provide:
        
        1. PORTFOLIO ASSESSMENT:
           - Overall health and performance evaluation
           - Key strengths and vulnerabilities
           - Correlation with broader market trends
        
        2. ACTIONABLE RECOMMENDATIONS:
           - Specific stocks to consider buying, holding, or selling
           - Potential new sectors or assets to explore
           - Rebalancing suggestions with percentages
           - Clear reasoning for each recommendation
        
        3. MARKET OUTLOOK:
           - How recent news might impact the portfolio
           - Sectors to watch in the near term
           - Potential risks and opportunities
        
        Be specific, data-driven, and provide clear reasoning for all recommendations.
        Focus on practical advice that can be implemented immediately.
        """
        
        # Format data for prompt
        formatted_metrics = json.dumps(performance_metrics, indent=2)
        formatted_suggestions = "\n".join([f"- {s['type']} ({s['severity']}): {s['action']} for {s['symbol']} - {s['reasoning']}" for s in suggestions])
        
        prompt = prompt_template.format(
            performance_metrics=formatted_metrics,
            suggestions=formatted_suggestions,
            news_summary=news_summary
        )
        
        # Get decision report from LLM
        decision_report = self.llm.generate_content(prompt)
        
        # Save decision report
        today = datetime.now().strftime("%Y-%m-%d")
        with open(os.path.join(self.decisions_dir, f"portfolio_decisions_{today}.md"), "w", encoding="utf-8") as f:
            f.write(decision_report)
        
        return decision_report
