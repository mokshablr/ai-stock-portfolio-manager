# Create a sample portfolio.json file
import json

sample_portfolio = {
  "stocks": [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "HINDUNILVR", "KOTAKBANK", "ITC", "LT", "MARUTI"
  ],
  "holdings": {
    "RELIANCE": 10,
    "TCS": 15,
    "INFY": 20,
    "HDFCBANK": 25,
    "ICICIBANK": 30,
    "HINDUNILVR": 35,
    "KOTAKBANK": 40,
    "ITC": 45,
    "LT": 50,
    "MARUTI": 55
  },
  "company_names": {
    "RELIANCE": "Reliance Industries Limited",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys Limited",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever Limited",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "ITC": "ITC Limited",
    "LT": "Larsen & Toubro Limited",
    "MARUTI": "Maruti Suzuki India Limited"
  },
  "sectors": {
    "RELIANCE": "Conglomerate - Energy, Retail, Telecom",
    "TCS": "IT Services & Consulting",
    "INFY": "IT Services & Consulting",
    "HDFCBANK": "Private Sector Banking",
    "ICICIBANK": "Private Sector Banking",
    "HINDUNILVR": "FMCG - Consumer Goods",
    "KOTAKBANK": "Private Sector Banking",
    "ITC": "Conglomerate - FMCG, Hotels, Paperboards",
    "LT": "Engineering & Construction",
    "MARUTI": "Automobile - Passenger Vehicles"
  },
  "average_cost": {
    "RELIANCE": 2500.00,
    "TCS": 3500.00,
    "INFY": 1500.00,
    "HDFCBANK": 1600.00,
    "ICICIBANK": 800.00,
    "HINDUNILVR": 2500.00,
    "KOTAKBANK": 1800.00,
    "ITC": 300.00,
    "LT": 2000.00,
    "MARUTI": 7000.00
  }
}

# Write to file
with open("my-portfolio.json", "w", encoding="utf-8") as f:
    json.dump(sample_portfolio, f, indent=2)

print("Sample portfolio file created: portfolio.json")
