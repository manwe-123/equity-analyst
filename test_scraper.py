from sec_scraper import SECScraper

def main():
    scraper = SECScraper()
    tickers_to_test = ["MU", "AAPL"]
    
    for ticker in tickers_to_test:
        print(f"\n=== Testing {ticker} ===")
        risk_factors = scraper.get_risk_factors(ticker)
        
        if "failed" in risk_factors.lower() or "not found" in risk_factors.lower():
            print(f"❌ Result: {risk_factors}")
        else:
            print(f"✅ SUCCESS! Extracted {len(risk_factors)} characters.")
            print(f"Preview: {risk_factors[:200]}...")
            
if __name__ == "__main__":
    main()