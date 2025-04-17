**AI Portfolio Analyzer for Indian Stocks**  
An AI-driven workflow to monitor, analyze, and optimize your Indian stock portfolio using free tools and local LLM inference via Ollama.

---

## 🚀 Features

- **Portfolio Performance Analysis**: Calculates total and annualized returns, volatility, Sharpe ratio, and max drawdown.
- **Stock Contributions**: Analyzes individual stock returns, weights, correlation to market, beta, and key financial metrics.
- **Optimization Suggestions**: Recommendations for diversification, underperformance, and risk-adjusted rebalancing.
- **News Integration**: Fetches and categorizes recent news via RSS (Google News) or NewsAPI (optional), then summarizes via local LLM.
- **Decision Engine**: Generates data-driven, reasoning-backed portfolio advice using your local Ollama LLM.
- **Daily Reporting & Scheduling**: Produces Markdown reports and visualizations; supports on-demand runs or cron-like scheduling.
- **PDF Report Generation**: Creates comprehensive daily reports in PDF format with performance metrics, stock returns, news summaries, and optimization suggestions. Additionally, generates a text summary for messaging.

---

## 🛠 Tech Stack & Free Services

- **Python 3.8+**
- **yfinance**: Stock price & financial metrics (free)  
- **feedparser**: RSS news scraping (free)  
- **NewsAPI.org** (optional; free tier)  
- **Ollama**: Local LLM inference (e.g., llama3)  
- **schedule**: Job scheduling in Python  
- **fpdf**: PDF generation for reports  
- **matplotlib**: Data visualization  
- **Environment Variables**: Managed via `.env` and `python-dotenv`

---

## ⚙️ Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/mokshablr/ai-stock-portfolio-manager.git
    cd ai-stock-portfolio-manager
    ```

2. **Create & activate a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\\Scripts\\activate  # Windows
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**  
   Copy the example and fill in any API keys:
    ```bash
    cp .env.example .env
    # Edit .env: set NEWS_API_KEY, OLLAMA_API_ENDPOINT, etc.
    ```

5. **Run Ollama local model**  
   Ensure Ollama is installed and running:
    ```bash
    ollama run llama3
    ```

---

## 📁 Repository Structure

```
├── data_cache/                # Cached stock & news data
├── portfolio_ai/              # Workflow outputs & history
│   └── run_history.json
├── analysis_results/          # Performance & contribution JSONs, CSVs, plots
├── decision_reports/          # LLM-generated decision Markdown files
├── news_reports/              # Categorized news & summaries
├── generated_reports/         # Generated PDF and Markdown reports
├── src/                       # Main source files (optional grouping)
│   ├── data_collector.py      # Fetches stock & news data
│   ├── portfolio_analyser.py  # Calculates performance & suggestions
│   ├── news_aggregator.py     # Categorizes & summarizes news
│   ├── llm_connector.py       # Interfaces with local LLM & DecisionEngine
│   ├── report_generator.py    # Generates PDF and text reports (portfolio performance, suggestions, news summaries)
│   ├── portfolio_ai_workflow.py # Orchestrates full workflow
│   └── main.py                # CLI entry point
├── .env.example               # Example environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Usage

### 1. On-Demand Run

```bash
python main.py --portfolio path/to/portfolio.json
```

This outputs summary in console and writes detailed reports in respective directories.

### 2. Schedule Daily Runs

```bash
python main.py --schedule --time 18:00
```

This runs the full workflow every day at 18:00 local time.

---

## 📄 Configuration

Your `portfolio.json` file should either be created manually in the following format or generated automatically using `sample_portfolio_generator.py`:
```json
{
  "stocks": ["RELIANCE", "INFY", "TCS"],
  "holdings": {"RELIANCE": 10, "INFY": 5, "TCS": 8},
  "avg_costs": {"RELIANCE": 2400.50, "INFY": 1450.00, "TCS": 3300.00},
  "company_names": {"RELIANCE": "Reliance Industries Limited", ...}
}
```

Ensure `.env` contains:
```
NEWS_API_KEY=your_newsapi_key
OLLAMA_API_ENDPOINT=your_ollama_endpoint
```

---

## 🔍 Example Output

- **Analysis Results**: `analysis_results/portfolio_performance.csv`, `performance_metrics.json`, `stock_contributions.json`  
- **Visualizations**: `analysis_results/portfolio_composition.png`, `portfolio_performance.png`, `stock_returns.png`  
- **News Summary**: `news_reports/news_summary_YYYY-MM-DD.md`  
- **Decision Report**: `decision_reports/portfolio_decisions_YYYY-MM-DD.md`  
- **Generated Reports**: `generated_reports/portfolio_report_YYYY-MM-DD.pdf`, `generated_reports/summary_YYYY-MM-DD.md`

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.