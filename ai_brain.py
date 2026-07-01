import ollama
import json

class AIAnalyst:
    def __init__(self, model_name="llama3.1"):
        """
        Initialize the AI Analyst with a specific model.
        """
        self.model_name = model_name
        print(f"AI Analyst initialized with model: {self.model_name}")

    def analyze_news(self, articles_text, sector="general"):
        """
        Takes a string of news articles, sends it to the LLM with a strict 
        system prompt, and returns the parsed JSON data.
        """
        system_prompt = f"""
        You are an expert financial Information Extractor analyzing {sector.upper()} news. 
        You DO NOT give financial advice, and you DO NOT guess or hallucinate data.
        Your only job is to analyze the provided news headlines and extract structured data.
        
        You must respond with a STRICT JSON object containing exactly these keys:
        - "market_theme": A 1-sentence summary of the dominant theme in the news.
        - "overall_sentiment": A string, either "Bullish", "Bearish", or "Neutral".
        - "relevant_tickers": A list of strings containing the stock tickers explicitly mentioned OR the standard ticker symbols for major public companies explicitly named in the text. Max 5 tickers.
        - "key_takeaway": A 1-sentence summary of the most important overall takeaway.
        - "key_risks": A list of exactly 2 specific risks mentioned or implied in the text.
        - "key_opportunities": A list of exactly 2 specific growth opportunities mentioned or implied in the text.
        
        CRITICAL RULE: Respond ONLY with the raw JSON object. Do not include greetings, explanations, or markdown formatting like ```json.
        """

        user_prompt = f"Please analyze the following financial news:\n\n{articles_text}"

        print("Sending data to local AI for analysis... (This may take 10-30 seconds)")

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format='json' 
            )
            
            raw_text = response['message']['content']
            parsed_data = json.loads(raw_text)
            return parsed_data

        except json.JSONDecodeError:
            print("Error: AI returned invalid JSON. Raw response:", raw_text)
            return None
        except Exception as e:
            print(f"An error occurred while talking to Ollama: {e}")
            return None

    def generate_quick_brief(self, ticker, articles_text):
        """
        A fast, lightweight AI prompt that won't hang your local Mac.
        """
        prompt = f"""
        You are a financial analyst. Read the following news articles about {ticker}.
        Write a concise, 3-bullet-point summary of the most important positive catalysts or negative risks mentioned.
        Keep it under 50 words total. Do not use JSON. Just use bullet points.
        """
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"News Context:\n{articles_text}"}
                ]
                # Notice we removed format='json' and complex structures. This runs in 2 seconds.
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"Failed to generate brief: {e}"
    
    def generate_confidence_score(self, ticker, quant_metrics, sec_risks, news_brief):
        """
        Synthesizes Quant, Legal, and News data into a final Confidence Score.
        """
        # Format the quant metrics into a readable string
        quant_str = f"""
        Price: ${quant_metrics.get('current_price')}, Trend: {quant_metrics.get('trend')}
        RSI: {quant_metrics.get('rsi_14')}, MACD Histogram: {quant_metrics.get('macd_histogram')}
        P/E: {quant_metrics.get('pe_ratio')}, PEG: {quant_metrics.get('peg_ratio')}
        ROE: {quant_metrics.get('roe')}, FCF: {quant_metrics.get('fcf')}, Rev Growth: {quant_metrics.get('revenue_growth')}
        """
                
        prompt = f"""
        You are a Senior Portfolio Manager on an Investment Committee.
        You are evaluating {ticker} for a potential swing trade.
        
        DATA:
        1. QUANTITATIVE: {quant_str}
        2. LEGAL RISKS (SEC 10-Q): {sec_risks[:1000]}... (Truncated for brevity)
        3. NEWS CATALYST: {news_brief}
        
        TASK:
        Provide a final investment verdict. Respond in STRICT JSON format with exactly these keys:
        - "verdict": A string, one of: "Strong Buy", "Buy", "Hold", "Sell".
        - "confidence_score": An integer from 1 to 100 representing your conviction level.
        - "primary_catalyst": The single biggest reason to buy this stock right now (max 1 sentence).
        - "dealbreaker_risk": The single biggest reason to avoid this stock based on the SEC filings (max 1 sentence).
        
        CRITICAL RULE: Respond ONLY with the raw JSON object. No markdown, no greetings.
        """
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": "Evaluate this stock."}],
                format='json'
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            return {"error": str(e), "verdict": "Hold", "confidence_score": 50}