from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
import re
import os
import shutil

class SECScraper:
    def __init__(self):
        self.dl = Downloader("EquityAnalystPortfolio", "student@asu.edu")
        self.download_dir = "./sec-edgar-filings"

    def get_risk_factors(self, ticker):
        print(f"🕵️ [SEC Scraper] Downloading latest 10-Q for {ticker}...")
        
        try:
            # 1. Download the filing
            self.dl.get("10-Q", ticker, download_details=True, limit=1)
            
            # 2. Locate the full-submission.txt file
            ticker_dir = os.path.join(self.download_dir, ticker, "10-Q")
            
            # Find the accession folder (it's the only subfolder inside the ticker dir)
            accession_folders = [f for f in os.listdir(ticker_dir) if os.path.isdir(os.path.join(ticker_dir, f))]
            if not accession_folders:
                return "No accession folder found."
                
            accession_dir = os.path.join(ticker_dir, accession_folders[0])
            full_submission_path = os.path.join(accession_dir, "full-submission.txt")
            
            if not os.path.exists(full_submission_path):
                return "full-submission.txt not found."
                
            print(f"📄 [Debug] Reading full-submission.txt...")
            
            # 3. Read the entire raw text file
            with open(full_submission_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 4. Split the content into individual document blocks
            # The SEC uses <DOCUMENT> tags to separate files inside the full submission
            documents = content.split('<DOCUMENT>')
            
            target_text = ""
            for doc in documents:
                # Find the specific block that is the 10-Q or 10-K
                if '<TYPE>10-Q' in doc.upper() or '<TYPE>10-K' in doc.upper():
                    target_text = doc
                    break
                    
            if not target_text:
                return "Could not find 10-Q/10-K document block in full-submission.txt."
                
            # 5. Parse the target document block with BeautifulSoup
            # BeautifulSoup is incredibly forgiving and will strip out the SGML headers
            # and just extract the human-readable HTML/text inside.
            soup = BeautifulSoup(target_text, 'html.parser')
            clean_text = soup.get_text(separator=' ', strip=True)
            
            # 6. Extract Risk Factors - Find ALL occurrences and pick the longest
            # This bypasses the Table of Contents entries (which are short)
            matches = re.findall(r'ITEM\s*1A[.\s]*RISK\s*FACTORS(.*?)(?=ITEM\s*1B[.\s]|ITEM\s*2[.\s])', clean_text, re.IGNORECASE | re.DOTALL)
            
            # 7. Cleanup
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
            
            if matches:
                # Pick the longest match (the actual content, not the TOC)
                risk_text = max(matches, key=len).strip()
                words = risk_text.split()
                if len(words) > 1500:
                    risk_text = " ".join(words[:1500]) + "..."
                return risk_text
            else:
                return "Risk Factors section not found in the filing."

        except Exception as e:
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
            return f"SEC Scraper failed: {e}"