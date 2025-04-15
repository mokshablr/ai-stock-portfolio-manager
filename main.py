import argparse
from portfolio_ai_workflow import PortfolioAIWorkflow

def main():
    parser = argparse.ArgumentParser(description='AI Portfolio Manager for Indian Stocks')
    parser.add_argument('--portfolio', type=str, default='portfolio.json',
                        help='Path to portfolio JSON file')
    parser.add_argument('--schedule', action='store_true',
                        help='Schedule daily runs')
    parser.add_argument('--time', type=str, default='18:00',
                        help='Time for scheduled runs (HH:MM)')
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = PortfolioAIWorkflow(portfolio_file=args.portfolio)
    
    if args.schedule:
        print(f"Scheduling daily runs at {args.time}")
        workflow.schedule_daily_run(args.time)
    else:
        print("Running workflow on demand")
        summary = workflow.run_on_demand()
        print("\nSUMMARY:")
        print(summary)

if __name__ == "__main__":
    main()
