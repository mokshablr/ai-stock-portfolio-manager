import json
import os
from datetime import datetime
import pandas as pd

class NewsAggregator:
    def __init__(self, data_collector, llm_connector):
        """
        Initialize the news aggregator
        data_collector: Instance of DataCollector class
        llm_connector: Instance of LLMConnector class for summarization
        """
        self.data_collector = data_collector
        self.llm = llm_connector
        self.news_dir = "news_reports"
        os.makedirs(self.news_dir, exist_ok=True)
    
    def fetch_and_categorize_news(self, days=3):
        """
        Fetch news and categorize by impact and relevance
        days: Number of past days to fetch news for
        """
        news_items = self.data_collector.fetch_news(days=days)
        portfolio_symbols = self.data_collector.portfolio["stocks"]
        
        # Categorize news
        categorized_news = {
            "high_impact": [],
            "medium_impact": [],
            "low_impact": [],
            "general_market": []
        }
        
        for item in news_items:
            if item["symbol"] == "MARKET":
                categorized_news["general_market"].append(item)
            elif item["symbol"] in portfolio_symbols:
                # This would be better with LLM assistance to categorize impact
                # For now, use a simple keyword-based approach
                title_lower = item["title"].lower()
                summary_lower = item["summary"].lower() if item["summary"] else ""
                
                high_impact_keywords = ["plunge", "surge", "crash", "soar", "record high", "record low",
                                       "major announcement", "acquisition", "merger", "scandal", "regulatory"]
                medium_impact_keywords = ["earnings", "results", "guidance", "outlook", "forecast", 
                                         "expansion", "partnership", "new product", "dividend"]
                
                if any(keyword in title_lower or keyword in summary_lower for keyword in high_impact_keywords):
                    categorized_news["high_impact"].append(item)
                elif any(keyword in title_lower or keyword in summary_lower for keyword in medium_impact_keywords):
                    categorized_news["medium_impact"].append(item)
                else:
                    categorized_news["low_impact"].append(item)
        
        # Save categorized news
        with open(os.path.join(self.news_dir, "categorized_news.json"), "w") as f:
            json.dump(categorized_news, f, indent=2)
        
        return categorized_news
    
    def summarize_news(self, categorized_news=None):
        """
        Summarize news using LLM
        categorized_news: Pre-categorized news dict (if None, will fetch new)
        """
        if categorized_news is None:
            categorized_news = self.fetch_and_categorize_news()
        
        # Prepare news for summarization
        high_impact_news = categorized_news["high_impact"]
        medium_impact_news = categorized_news["medium_impact"]
        market_news = categorized_news["general_market"]
        
        # Prepare prompt for LLM
        prompt_template = """
        Please analyze and summarize the following financial news articles. 
        Focus on practical implications for an Indian stock market investor.
        
        HIGH IMPACT NEWS:
        {high_impact_news}
        
        MEDIUM IMPACT NEWS:
        {medium_impact_news}
        
        GENERAL MARKET NEWS:
        {market_news}
        
        Provide a concise summary with the following sections:
        1. Key Takeaways (bullet points)
        2. Potential Impact on Portfolio (brief paragraph)
        3. Stocks to Watch (list specific stocks mentioned and why)
        """
        
        # Format news for prompt
        formatted_high_impact = "\n".join([f"- {item['title']} (Source: {item['source']})" for item in high_impact_news[:5]])
        formatted_medium_impact = "\n".join([f"- {item['title']} (Source: {item['source']})" for item in medium_impact_news[:5]])
        formatted_market = "\n".join([f"- {item['title']} (Source: {item['source']})" for item in market_news[:5]])
        
        prompt = prompt_template.format(
            high_impact_news=formatted_high_impact if formatted_high_impact else "None",
            medium_impact_news=formatted_medium_impact if formatted_medium_impact else "None",
            market_news=formatted_market if formatted_market else "None"
        )
        
        # Get summary from LLM
        summary = self.llm.generate_content(prompt)
        
        # Save summary
        today = datetime.now().strftime("%Y-%m-%d")
        with open(os.path.join(self.news_dir, f"news_summary_{today}.md"), "w") as f:
            f.write(summary)
        
        return summary
