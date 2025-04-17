import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import json
import feedparser
from dotenv import load_dotenv

load_dotenv()

class DataCollector:
    def __init__(self, portfolio_file="portfolio.json"):
        """
        Initialize the data collector with your portfolio
        portfolio_file: JSON file with stock symbols and quantities
        """
        self.portfolio = self._load_portfolio(portfolio_file)
        self.cache_dir = "data_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _load_portfolio(self, file_path):
        """Load portfolio from JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)
        
    def fetch_nifty_data(self, timeframe="1mo"):
        """
        Fetch Nifty 50 index data
        timeframe: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
        """
        print("DataCollector | Fetching Nifty data...")
        nifty_symbol = "^NSEI"
        try:
            nifty_data = yf.Ticker(nifty_symbol)
            hist = nifty_data.history(period=timeframe)
            cache_path = os.path.join(self.cache_dir, "nifty_data.csv")
            hist.to_csv(cache_path)
            print("DataCollector | Successfully fetched Nifty data")
            return hist
        except Exception as e:
            print(f"DataCollector | Error fetching Nifty data: {e}")
            return None
    
    def fetch_stock_data(self, timeframe="1mo"):
        """
        Fetch historical stock data for all portfolio stocks
        timeframe: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
        """
        print("DataCollector | Fetching stock data...")
        stock_data = {}
        for symbol in self.portfolio["stocks"]:
            # For Indian stocks, append .NS for NSE listings
            ticker_symbol = f"{symbol}.NS"
            try:
                # Get data from Yahoo Finance
                ticker_data = yf.Ticker(ticker_symbol)
                hist = ticker_data.history(period=timeframe)
                stock_data[symbol] = hist
                
                # Cache the data
                cache_path = os.path.join(self.cache_dir, f"{symbol}_data.csv")
                hist.to_csv(cache_path)
                
                print(f"DataCollector | Successfully fetched data for {symbol}")
            except Exception as e:
                print(f"DataCollector | Error fetching data for {symbol}: {e}")
        
        return stock_data
    
    def fetch_financial_metrics(self, symbol):
        """Fetch key financial metrics for a stock"""
        print(f"DataCollector | Fetching financial metrics for {symbol}...")
        ticker_symbol = f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        
        # Get financial info
        info = ticker.info
        
        # Get key metrics
        metrics = {
            "PE Ratio": info.get("trailingPE", None),
            "Market Cap": info.get("marketCap", None),
            "52W High": info.get("fiftyTwoWeekHigh", None),
            "52W Low": info.get("fiftyTwoWeekLow", None),
            "Dividend Yield": info.get("dividendYield", None),
            "Return on Equity": info.get("returnOnEquity", None),
            "Debt to Equity": info.get("debtToEquity", None)
        }
        
        return metrics
    

    def fetch_news(self, symbols=None, days=3, source="rss"):
        """
        Fetch news from selected source (rss or newsapi) for specified stocks.
        
        Args:
            symbols: List of stock symbols
            days: How many past days to fetch news for
            source: 'rss' (Google News RSS) or 'newsapi'
        """
        print(f"DataCollector | Fetching news with {source}...")
        if symbols is None:
            symbols = self.portfolio["stocks"]

        source = source.lower()
        if source == "newsapi":
            return self._fetch_newsapi_news(symbols, days)
        elif source == "rss":
            return self._fetch_rss_news(symbols, days)
        else:
            raise ValueError("DataCollector | Invalid news source. Choose 'rss' or 'newsapi'.")

    def _fetch_newsapi_news(self, symbols, days):
        print("DataCollector | Fetching news from NewsAPI...")
        news_api_key = os.getenv("NEWS_API_KEY")

        all_news = []
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        for symbol in symbols:
            company_name = self.portfolio.get("company_names", {}).get(symbol, symbol)
            url = (
                f"https://newsapi.org/v2/everything?q={company_name}"
                f"&from={from_date}&sortBy=publishedAt&apiKey={news_api_key}&language=en"
            )
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    for article in response.json().get("articles", []):
                        all_news.append({
                            "symbol": symbol,
                            "title": article.get("title"),
                            "source": article.get("source", {}).get("name"),
                            "published_at": article.get("publishedAt"),
                            "url": article.get("url"),
                            "summary": article.get("description"),
                        })
                else:
                    print(f"DataCollector | [NewsAPI] Error for {symbol}: {response.status_code}")
            except Exception as e:
                print(f"DataCollector | [NewsAPI] Exception for {symbol}: {e}")

        # General market news
        market_terms = ["NSE", "Sensex", "Nifty", "Indian stock market"]
        for term in market_terms:
            url = (
                f"https://newsapi.org/v2/everything?q={term}"
                f"&from={from_date}&sortBy=publishedAt&apiKey={news_api_key}&language=en"
            )
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    for article in response.json().get("articles", [])[:5]:
                        all_news.append({
                            "symbol": "MARKET",
                            "title": article.get("title"),
                            "source": article.get("source", {}).get("name"),
                            "published_at": article.get("publishedAt"),
                            "url": article.get("url"),
                            "summary": article.get("description"),
                        })
            except Exception as e:
                print(f"DataCollector | [NewsAPI] Exception for market term '{term}': {e}")

        return self._finalize_news(all_news)

    def _fetch_rss_news(self, symbols, days):
        print("DataCollector | Fetching news from RSS...")
        all_news = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for symbol in symbols:
            company_name = self.portfolio.get("company_names", {}).get(symbol, symbol)
            query = company_name.replace(" ", "+")
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries:
                    published_at = datetime(*entry.published_parsed[:6])
                    if published_at >= cutoff_date:
                        all_news.append({
                            "symbol": symbol,
                            "title": entry.title,
                            "source": entry.get("source", {}).get("title", "Google News"),
                            "published_at": published_at.isoformat(),
                            "url": entry.link,
                            "summary": entry.get("summary", ""),
                        })
            except Exception as e:
                print(f"DataCollector | [RSS] Error fetching news for {symbol}: {e}")

        # General market news
        market_terms = ["NSE", "Sensex", "Nifty", "Indian stock market"]
        for term in market_terms:
            query = term.replace(" ", "+")
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:5]:
                    published_at = datetime(*entry.published_parsed[:6])
                    if published_at >= cutoff_date:
                        all_news.append({
                            "symbol": "MARKET",
                            "title": entry.title,
                            "source": entry.get("source", {}).get("title", "Google News"),
                            "published_at": published_at.isoformat(),
                            "url": entry.link,
                            "summary": entry.get("summary", ""),
                        })
            except Exception as e:
                print(f"DataCollector | [RSS] Error fetching market news for {term}: {e}")

        return self._finalize_news(all_news)

    def _finalize_news(self, all_news):
        print("DataCollector | Finalizing news data...")
        all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(os.path.join(self.cache_dir, "latest_news.json"), "w", encoding="utf-8") as f:
                json.dump(all_news, f, indent=2)
        except Exception as e:
            print(f"DataCollector | [Cache] Error writing news to cache: {e}")

        return all_news


# Example usage
if __name__ == "__main__":
    collector = DataCollector()
    stock_data = collector.fetch_stock_data()
    news = collector.fetch_news()
    
    # Example for one stock
    metrics = collector.fetch_financial_metrics("RELIANCE")  # Reliance Industries
    print(metrics)
