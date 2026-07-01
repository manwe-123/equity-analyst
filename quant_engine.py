import yfinance as yf
import pandas as pd
import ta

class QuantEngine:
    def get_deep_analysis(self, ticker_symbol):
        """
        Pulls 1 year of historical data and calculates advanced technical & fundamental metrics.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # 1. Fetch 1 year of historical data for technicals
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
                
            close_prices = hist['Close']
            current_price = close_prices.iloc[-1]
            
            # --- ADVANCED TECHNICALS ---
            
            # RSI (Relative Strength Index)
            rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi().iloc[-1]
            
            # MACD (Moving Average Convergence Divergence) - Momentum indicator
            macd_ind = ta.trend.MACD(close=close_prices)
            macd_line = macd_ind.macd().iloc[-1]
            macd_signal = macd_ind.macd_signal().iloc[-1]
            macd_histogram = macd_line - macd_signal
            
            # Bollinger Bands - Volatility indicator
            bb = ta.volatility.BollingerBands(close=close_prices, window=20, window_dev=2)
            bb_upper = bb.bollinger_hband().iloc[-1]
            bb_lower = bb.bollinger_lband().iloc[-1]
            bb_width = ((bb_upper - bb_lower) / current_price) * 100 # Normalized width
            
            # Trend Logic (SMA)
            sma_50 = ta.trend.SMAIndicator(close=close_prices, window=50).sma_indicator().iloc[-1]
            sma_200 = ta.trend.SMAIndicator(close=close_prices, window=200).sma_indicator().iloc[-1]
            trend = "Bullish" if current_price > sma_50 > sma_200 else "Bearish" if current_price < sma_50 < sma_200 else "Neutral"

            # --- ADVANCED FUNDAMENTALS ---
            info = ticker.info
            
            # Extract fundamentals with fallbacks
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            peg_ratio = info.get('pegRatio')
            roe = info.get('returnOnEquity') # Return on Equity
            fcf = info.get('freeCashflow') # Free Cash Flow
            revenue_growth = info.get('revenueGrowth')
            debt_to_equity = info.get('debtToEquity')
            
            # Format numbers for UI
            roe_str = f"{roe * 100:.2f}%" if roe else "N/A"
            fcf_str = f"${fcf / 1e9:.2f}B" if fcf else "N/A"
            rev_growth_str = f"{revenue_growth * 100:.2f}%" if revenue_growth else "N/A"
            debt_to_equity_str = f"{debt_to_equity / 100:.2f}" if debt_to_equity else "N/A"

            return {
                "symbol": ticker_symbol,
                "current_price": round(current_price, 2),
                "rsi_14": round(rsi, 2),
                "trend": trend,
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
                "peg_ratio": round(peg_ratio, 2) if peg_ratio else "N/A",
                "roe": roe_str,
                "fcf": fcf_str,
                "revenue_growth": rev_growth_str,
                "debt_to_equity": debt_to_equity_str,
                # Technicals
                "macd_histogram": round(macd_histogram, 3),
                "bb_width": round(bb_width, 2),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2)
            }
        except Exception as e:
            print(f"⚠️ Quant Engine failed for {ticker_symbol}: {e}")
            return None