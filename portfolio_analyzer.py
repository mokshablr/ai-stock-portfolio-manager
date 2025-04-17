import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

class PortfolioAnalyzer:
    def __init__(self, data_collector):
        """
        Initialize the portfolio analyzer
        data_collector: Instance of DataCollector class
        """
        self.data_collector = data_collector
        self.portfolio = data_collector.portfolio
        self.results_dir = "analysis_results"
        self.nifty_data = data_collector.fetch_nifty_data("1y")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def calculate_portfolio_performance(self, stock_data=None, timeframe="1y"):
        """
        Calculate overall portfolio performance
        timeframe: Time period for performance calculation
        """
        print("PotfolioAnalyser | Calculating portfolio performance...")
        if stock_data is None:
            # Fetch stock data if not provided
            stock_data = self.data_collector.fetch_stock_data(timeframe)

        portfolio_value_history = []
        
        # Get date range from the first stock (assumes all stocks have same date range)
        first_stock = list(stock_data.values())[0]
        dates = first_stock.index
        
        # Calculate portfolio value for each date
        for date in dates:
            daily_value = 0
            for symbol, quantity in self.portfolio.get("holdings", {}).items():
                if symbol in stock_data and date in stock_data[symbol].index:
                    price = stock_data[symbol].loc[date, "Close"]
                    daily_value += price * quantity
            
            portfolio_value_history.append({
                "date": date,
                "value": daily_value
            })
        
        # Convert to DataFrame
        performance_df = pd.DataFrame(portfolio_value_history)
        performance_df.set_index("date", inplace=True)
        
        # Calculate daily returns
        performance_df["daily_return"] = performance_df["value"].pct_change()
        
        # Calculate cumulative returns
        initial_value = performance_df["value"].iloc[0]
        performance_df["cumulative_return"] = (performance_df["value"] / initial_value) - 1
        
        # Additional metrics
        total_return = performance_df["cumulative_return"].iloc[-1]
        annualized_return = (1 + total_return) ** (365 / len(performance_df)) - 1
        volatility = performance_df["daily_return"].std() * np.sqrt(252)  # Annualized volatility
        sharpe_ratio = annualized_return / volatility  # Simplified Sharpe ratio (assuming 0 risk-free rate)
        
        performance_metrics = {
            "total_return": total_return,
            "annualized_return": annualized_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": self._calculate_max_drawdown(performance_df["value"])
        }
        
        # Save results
        performance_df.to_csv(os.path.join(self.results_dir, "portfolio_performance.csv"))
        with open(os.path.join(self.results_dir, "performance_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(performance_metrics, f, indent=2)
        
        return performance_df, performance_metrics
    
    def _calculate_max_drawdown(self, price_series):
        """Calculate maximum drawdown from a price series"""
        print("PotfolioAnalyser | Calculating maximum drawdown...")
        roll_max = price_series.cummax()
        drawdown = (price_series / roll_max) - 1
        return drawdown.min()
    
    def analyze_stock_contributions(self, stock_data=None):
        """Analyze how each stock contributes to portfolio performance and risk"""
        print("PotfolioAnalyser | Analyzing stock contributions...")
        if stock_data is None:
            # Fetch stock data if not provided
            stock_data = self.data_collector.fetch_stock_data("1y")

        contributions = {}

        # Calculate total investment based on initial prices(start of fetched data)
        # total_investment = 0
        # for symbol, quantity in self.portfolio.get("holdings", {}).items():
        #     if symbol in stock_data:
        #         initial_price = stock_data[symbol]["Close"].iloc[0]
        #         total_investment += initial_price * quantity
        
        # Calculate total investment based on average buy cost basis (personalised)
        total_investment = 0
        for symbol, quantity in self.portfolio.get("holdings", {}).items():
            if symbol in stock_data:
                print(f"PotfolioAnalyser | Calculating initial investment for {symbol}...")
                avg_buy_price = self.portfolio["avg_costs"].get(symbol)
                initial_value = avg_buy_price * quantity
                total_investment += initial_value

        for symbol, quantity in self.portfolio.get("holdings", {}).items():
            if symbol in stock_data:
                # Get latest price
                latest_price = stock_data[symbol]["Close"].iloc[-1]

                # Get initial price (start of fetched data), 
                # else use average cost basis from avg_buy_price
                # initial_price = stock_data[symbol]["Close"].iloc[0]
                avg_buy_price = self.portfolio["avg_costs"].get(symbol)
                initial_price = avg_buy_price
                
                # Calculate metrics
                current_value = latest_price * quantity
                # initial_value = initial_price * quantity
                
                initial_value = initial_price * quantity

                weight = current_value / total_investment
                print(f"PotfolioAnalyser | Calculating stock return for {symbol}...")
                stock_return = (latest_price / initial_price) - 1
                print(f"PotfolioAnalyser | Stock return for {symbol}: {stock_return:.2%}")
                contribution_to_return = stock_return * weight
                
                print(f"PotfolioAnalyser | Calculating beta for {symbol}...")

                # Get stock beta (if available) or calculate
                # For simplicity, we'll use correlation to Nifty as a proxy for beta
                if self.nifty_data is not None:
                    stock_returns = stock_data[symbol]["Close"].pct_change().dropna()
                    nifty_returns = self.nifty_data["Close"].pct_change().dropna()
                    
                    # Align dates
                    aligned_data = pd.concat([stock_returns, nifty_returns], axis=1).dropna()
                    if not aligned_data.empty and len(aligned_data) > 30:  # Ensure enough data points
                        correlation = aligned_data.iloc[:, 0].corr(aligned_data.iloc[:, 1])
                        beta = correlation * (stock_returns.std() / nifty_returns.std())
                    else:
                        correlation = None
                        beta = None
                else:
                    correlation = None
                    beta = None
                
                # Get financial metrics
                print(f"PotfolioAnalyser | Calculating financial metrics for {symbol}...")
                metrics = self.data_collector.fetch_financial_metrics(symbol)
                
                # Store all data
                contributions[symbol] = {
                    "quantity": quantity,
                    "current_price": round(latest_price, 2), 
                    "current_value": round(current_value, 2),
                    "weight": weight,
                    "return": round(stock_return, 2),
                    "contribution_to_return": round(contribution_to_return, 2),
                    "correlation_to_market": correlation,
                    "beta": beta,
                    "financial_metrics": metrics
                }
        
        # Save results
        with open(os.path.join(self.results_dir, "stock_contributions.json"), "w", encoding="utf-8") as f:
            json.dump(contributions, f, indent=2)

        print(f"PotfolioAnalyser | Stock contributions analysis complete. Found {len(contributions)} stocks.")
        return contributions
    
    def generate_optimization_suggestions(self, performance, contributions:dict, stock_data=None):
        """
        Generate portfolio optimization suggestions based on analysis
        Uses simple rules for now - will be enhanced with LLM in the next module
        """
        print("PotfolioAnalyser | Generating optimization suggestions...")
        performance_df, metrics = performance
        
        # Simple rule-based suggestions
        suggestions = []
        
        # 1. Check for overconcentration (any stock > 20% of portfolio)
        for symbol, data in contributions.items():
            if data["weight"] > 0.20:
                suggestions.append({
                    "type": "Diversification",
                    "symbol": symbol,
                    "action": "Consider reducing position",
                    "reasoning": f"{symbol} makes up {data['weight']:.1%} of your portfolio, which may increase concentration risk.",
                    "severity": "medium"
                })

        nifty_prices = self.nifty_data["Close"]

        # 2. Check for underperforming stocks (negative return and underperforming market)
        market_return = (nifty_prices.iloc[-1] / nifty_prices.iloc[0]) - 1
        for symbol, data in contributions.items():
            if data["return"] < 0 and data["return"] < market_return - 0.05:
                suggestions.append({
                    "type": "Performance",
                    "symbol": symbol,
                    "action": "Consider replacing or reducing",
                    "reasoning": f"{symbol} has returned {data['return']:.1%}, underperforming the market by {market_return - data['return']:.1%}.",
                    "severity": "high" if data["return"] < -0.10 else "medium"
                })
        
        # 3. Check for potential sector rebalancing
        # (This would require sector information - simplified here)
        
        # 4. Correlation/diversification checks
        high_correlation_pairs = []
        symbols = list(contributions.keys())
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                sym1, sym2 = symbols[i], symbols[j]
                corr1 = contributions[sym1].get("correlation_to_market")
                corr2 = contributions[sym2].get("correlation_to_market")
                if corr1 and corr2 and abs(corr1 - corr2) < 0.2:
                    high_correlation_pairs.append((sym1, sym2))
        
        if high_correlation_pairs:
            suggestions.append({
                "type": "Correlation",
                "symbol": ", ".join([f"{p[0]}/{p[1]}" for p in high_correlation_pairs[:3]]),
                "action": "Consider replacing one from each pair",
                "reasoning": "These pairs of stocks show similar correlation patterns and may not provide optimal diversification.",
                "severity": "low"
            })
        
        # 5. Overall portfolio assessment
        if metrics["sharpe_ratio"] < 0.5:
            suggestions.append({
                "type": "Portfolio",
                "symbol": "OVERALL",
                "action": "Consider risk/return optimization",
                "reasoning": f"Portfolio Sharpe ratio is {metrics['sharpe_ratio']:.2f}, indicating suboptimal risk-adjusted returns.",
                "severity": "medium" 
            })
        
        # Save suggestions
        with open(os.path.join(self.results_dir, "optimization_suggestions.json"), "w", encoding="utf-8") as f:
            json.dump(suggestions, f, indent=2)
        
        return suggestions
    
    def visualize_portfolio(self, contributions=None, performance=None):
        """Create visualizations of portfolio composition and performance"""
        print("PotfolioAnalyser | Generating visualizations...")
        if contributions is None:
            contributions = self.analyze_stock_contributions()
        if performance is None:
            performance_df, _ = self.calculate_portfolio_performance()
        
        performance_df, _ = performance
        
        # 1. Portfolio composition pie chart
        plt.figure(figsize=(10, 6))
        labels = [f"{symbol} ({data['weight']:.1%})" for symbol, data in contributions.items()]
        sizes = [data["weight"] for symbol, data in contributions.items()]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Portfolio Composition')
        plt.savefig(os.path.join(self.results_dir, "portfolio_composition.png"))
        plt.close()
        
        # 2. Performance over time
        plt.figure(figsize=(12, 6))
        plt.plot(performance_df.index, performance_df["cumulative_return"] * 100)
        plt.title('Portfolio Cumulative Return (%)')
        plt.xlabel('Date')
        plt.ylabel('Return (%)')
        plt.grid(True)
        plt.savefig(os.path.join(self.results_dir, "portfolio_performance.png"))
        plt.close()
        
        # 3. Individual stock returns comparison
        plt.figure(figsize=(12, 8))
        returns = []
        symbols = []
        for symbol, data in contributions.items():
            returns.append(data["return"] * 100)
            symbols.append(symbol)
        
        # Sort by return
        sorted_indices = np.argsort(returns)
        returns = [returns[i] for i in sorted_indices]
        symbols = [symbols[i] for i in sorted_indices]
        
        colors = ['g' if r >= 0 else 'r' for r in returns]
        plt.barh(symbols, returns, color=colors)
        plt.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        plt.title('Individual Stock Returns (%)')
        plt.xlabel('Return (%)')
        plt.grid(True, axis='x')
        plt.savefig(os.path.join(self.results_dir, "stock_returns.png"))
        plt.close()
        
        return "Visualizations saved to analysis_results directory"

# Example usage
if __name__ == "__main__":
    from data_collector import DataCollector
    collector = DataCollector()
    analyzer = PortfolioAnalyzer(collector)
    
    # Run analysis
    performance = analyzer.calculate_portfolio_performance()
    contributions = analyzer.analyze_stock_contributions()
    suggestions = analyzer.generate_optimization_suggestions()
    visualizations = analyzer.visualize_portfolio()
    
    print(f"PotfolioAnalyser | Analysis complete. Found {len(suggestions)} optimization suggestions.")
