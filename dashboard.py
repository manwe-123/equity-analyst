from news_parser import NewsParser
from quant_engine import QuantEngine
from sec_scraper import SECScraper
import streamlit as st
import pandas as pd
from collections import Counter
import fetch_news
from ai_brain import AIAnalyst
from market_data import MarketData
from data_manager import DataManager
from hardware_bridge import ArduinoBridge

# 1. Page Configuration
st.set_page_config(page_title="Hybrid Quant Analyst", layout="wide", page_icon="📈")

def main():
    # ==========================================
    # SIDEBAR: Controls
    # ==========================================
    with st.sidebar:
        st.title("⚙️ Control Panel")
        st.markdown("Configure your market analysis parameters.")
        st.divider()

        sector_map = {
            "Technology": "technology",
            "Business": "business",
            "Healthcare": "health",
            "Science": "science",
            "General Market": "general"
        }
        
        selected_pretty_sector = st.selectbox(
            "Target Sector", 
            options=list(sector_map.keys()),
            index=0
        )
        api_sector = sector_map[selected_pretty_sector]
        
        st.divider()
        st.subheader(" Search & Discovery")
        
        # 1. Targeted Search
        search_ticker = st.text_input("Analyze Specific Ticker", placeholder="e.g., TSLA, AAPL").upper()
        
        # 2. Auto-Discovery Toggle
        auto_discover = st.checkbox("Auto-Discover Top 5 Tickers from News", value=True)
        
        st.divider()
        run_button = st.button(f"🚀 Run Hybrid Analysis", type="primary", use_container_width=True)
        
        st.divider()
        st.caption("Powered by Local LLM (Llama 3.1) & yfinance")

    # ==========================================
    # MAIN CANVAS: The Dashboard
    # ==========================================
    st.title(f" {selected_pretty_sector} Hybrid Quant Analyst")
    st.markdown("Mathematical upside screening combined with AI news catalyst analysis.")
    st.divider()

    if run_button:
        # 1. Fetch Data
        with st.spinner(f"Fetching latest {selected_pretty_sector} news..."):
            raw_data = fetch_news.fetch_news_by_sector(sector=api_sector)
            
        if raw_data and raw_data.get("status") == "ok":
            # CRITICAL FIX: Define articles RIGHT HERE, before the loop!
            articles = raw_data.get("articles", [])[:30] 
            st.session_state['raw_articles'] = articles
            
            # 2. DYNAMIC DISCOVERY: Parse the news to find relevant companies
            print(f"🔍 [Discovery Engine] Scanning {len(articles)} articles for company mentions...")
            news_parser = NewsParser()
            watchlist = news_parser.extract_tickers(articles)
            
            if not watchlist:
                st.warning("No specific companies were found in today's news. Falling back to default watchlist.")
                watchlist = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM"]
                
            print(f"🎯 [Discovery Engine] Found {len(watchlist)} relevant tickers: {watchlist}")
            
            # 3. Initialize the progress bar explicitly
            progress_bar = st.progress(0, text="Initializing engines...")
            
            quant_engine = QuantEngine()
            sec_scraper = SECScraper()
            analyst = AIAnalyst()
            
            stock_data = []
            total_stocks = len(watchlist)
            
            # 4. The Synthesis Loop
            for i, ticker in enumerate(watchlist):
                progress_bar.progress((i + 1) / total_stocks, text=f"Analyzing {ticker}...")
                
                # A. Get Quant Data
                metrics = quant_engine.get_deep_analysis(ticker)
                if not metrics:
                    continue
                    
                # B. Filter News
                relevant_articles = []
                for article in articles:
                    title = (article.get('title') or '').upper()
                    desc = (article.get('description') or '').upper()
                    if ticker in title or ticker in desc:
                        relevant_articles.append(article)
                
                # C. Get News Brief
                brief_text = "No recent news found."
                if relevant_articles:
                    brief_text = "\n".join([f"- {art.get('title')}" for art in relevant_articles[:3]])
                    brief_text = analyst.generate_quick_brief(ticker, brief_text)
                    
                # D. Get SEC Risk Factors
                sec_risks = sec_scraper.get_risk_factors(ticker)
                
                # E. Generate Confidence Score (The Synthesis)
                confidence_data = analyst.generate_confidence_score(ticker, metrics, sec_risks, brief_text)
                
                stock_data.append({
                    "metrics": metrics,
                    "brief": brief_text,
                    "sec_risks": sec_risks,
                    "confidence": confidence_data,
                    "article_count": len(relevant_articles)
                })

            # 5. Sort by Confidence Score (Highest first)
            stock_data.sort(key=lambda x: x['confidence'].get('confidence_score', 0), reverse=True)
            st.session_state['stock_data'] = stock_data
            st.toast("Synthesis Complete!", icon="🏆")
        else:
            st.error("Failed to fetch news. Check terminal for API errors.")

    # 2. Render the UI (If we have data)
    if 'stock_data' in st.session_state and st.session_state['stock_data']:
        stock_data = st.session_state['stock_data']
        articles = st.session_state.get('raw_articles', [])

        tab1, tab2 = st.tabs(["🚀 High Upside Screener", "📰 Raw News Feed"])

        with tab1:
            st.subheader("🚀 High Upside / Turnaround Screener")
            st.markdown("Stocks mathematically far from their 52-week highs, filtered for recent news catalysts.")
            
            # Helper function to get score emoji
            def get_score_emoji(score, max_score):
                if max_score == 0:
                    return "⚪️"
                pct = (score / max_score) * 100
                if pct > 60:
                    return "🟢"
                elif pct >= 30:
                    return "🟡"
                else:
                    return "🔴"
            
            for stock in stock_data:
                m = stock['metrics']
                conf = stock['confidence']
                
                # Determine UI colors based on verdict
                verdict = conf.get('verdict', 'Hold')
                if 'Strong Buy' in verdict:
                    color = "🟢"
                elif 'Buy' in verdict:
                    color = "🟢"
                elif 'Sell' in verdict:
                    color = "🔴"
                else:
                    color = "⚪️"
                
                with st.container(border=True):
                    # 1. Header Section
                    col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
                    with col_h1:
                        st.markdown(f"### {color} ${m['symbol']}")
                        trend_info = m.get('technical_summary', {})
                        trend = trend_info.get('trend', 'N/A')
                        trend_strength = trend_info.get('trend_strength', 'N/A')
                        st.caption(f"Trend: {trend} ({trend_strength})")
                    with col_h2:
                        st.metric("Quant Score", f"{m.get('normalized_score', 'N/A')}/100")
                    with col_h3:
                        st.metric("Price", f"${m.get('current_price', 'N/A')}")
                    
                    st.divider()
                    
                    # 2. Factor Breakdown (5 columns)
                    c_val, c_mom, c_qual, c_size, c_vol = st.columns(5)
                    
                    # Value Factor (max 15)
                    with c_val:
                        with st.container(border=True):
                            value_data = m.get('value', {})
                            val_score = value_data.get('score', 0)
                            st.markdown("**Value**")
                            st.markdown(f"{get_score_emoji(val_score, 15)} Score: {val_score}/15")
                            st.caption(f"P/E: {value_data.get('pe_ratio') or 'N/A'}")
                            st.caption(f"PEG: {value_data.get('peg_ratio') or 'N/A'}")
                            st.caption(f"FCF Yield: {value_data.get('fcf_yield') or 'N/A'}%")
                            st.caption(f"EV/EBITDA: {value_data.get('ev_ebitda') or 'N/A'}")
                    
                    # Momentum Factor (max 12)
                    with c_mom:
                        with st.container(border=True):
                            mom_data = m.get('momentum', {})
                            mom_score = mom_data.get('score', 0)
                            st.markdown("**Momentum**")
                            st.markdown(f"{get_score_emoji(mom_score, 12)} Score: {mom_score}/12")
                            st.caption(f"RSI: {mom_data.get('rsi_14') or 'N/A'}")
                            st.caption(f"MACD Hist: {mom_data.get('macd_histogram') or 'N/A'}")
                            st.caption(f"vs SMA50: {mom_data.get('price_vs_sma50') or 'N/A'}")
                            st.caption(f"vs 52w High: {mom_data.get('proximity_to_52w_high') or 'N/A'}")
                    
                    # Quality Factor (max 18)
                    with c_qual:
                        with st.container(border=True):
                            qual_data = m.get('quality', {})
                            qual_score = qual_data.get('score', 0)
                            st.markdown("**Quality**")
                            st.markdown(f"{get_score_emoji(qual_score, 18)} Score: {qual_score}/18")
                            st.caption(f"ROE: {qual_data.get('roe') or 'N/A'}%")
                            st.caption(f"ROIC: {qual_data.get('roic') or 'N/A'}%")
                            st.caption(f"D/E: {qual_data.get('debt_to_equity') or 'N/A'}")
                            st.caption(f"Op Margin: {qual_data.get('operating_margin') or 'N/A'}%")
                    
                    # Size Factor (max 5)
                    with c_size:
                        with st.container(border=True):
                            size_data = m.get('size', {})
                            size_score = size_data.get('score', 0)
                            st.markdown("**Size**")
                            st.markdown(f"{get_score_emoji(size_score, 5)} Score: {size_score}/5")
                            st.caption(f"Category: {size_data.get('market_cap_category') or 'N/A'}")
                            st.caption(f"Revenue Growth: {size_data.get('revenue_growth') or 'N/A'}%")
                    
                    # Volatility Factor (max 9)
                    with c_vol:
                        with st.container(border=True):
                            vol_data = m.get('volatility', {})
                            vol_score = vol_data.get('score', 0)
                            st.markdown("**Volatility**")
                            st.markdown(f"{get_score_emoji(vol_score, 9)} Score: {vol_score}/9")
                            st.caption(f"Beta: {vol_data.get('beta') or 'N/A'}")
                            st.caption(f"BB Width: {vol_data.get('bollinger_width') or 'N/A'}%")
                            st.caption(f"Max DD: {vol_data.get('max_drawdown_1y') or 'N/A'}%")
                    
                    st.divider()
                    
                    # 3. Bottom Section: Risk-Adjusted & Technical Summary
                    c_risk, c_tech = st.columns(2)
                    
                    with c_risk:
                        st.markdown("**Risk-Adjusted Performance**")
                        risk_data = m.get('risk_adjusted', {})
                        st.caption(f"Sharpe Ratio: {risk_data.get('sharpe_ratio') or 'N/A'}")
                        st.caption(f"Sortino Ratio: {risk_data.get('sortino_ratio') or 'N/A'}")
                        st.caption(f"Calmar Ratio: {risk_data.get('calmar_ratio') or 'N/A'}")
                    
                    with c_tech:
                        st.markdown("**Technical Summary**")
                        tech_data = m.get('technical_summary', {})
                        st.caption(f"Trend: {tech_data.get('trend') or 'N/A'}")
                        st.caption(f"Strength: {tech_data.get('trend_strength') or 'N/A'}")
                        vol_data = m.get('volatility', {})
                        st.caption(f"Beta: {vol_data.get('beta') or 'N/A'}")
                    
                    st.divider()
                    
                    # Top Line Catalyst & Risk (from AI confidence)
                    col_catalyst, col_risk = st.columns(2)
                    with col_catalyst:
                        st.markdown(f"**🚀 Primary Catalyst:** {conf.get('primary_catalyst', 'N/A')}")
                    with col_risk:
                        st.markdown(f"**⚠️ Dealbreaker Risk:** {conf.get('dealbreaker_risk', 'None')}")

        with tab2:
            st.subheader("Source Material")
            st.caption(f"The top {len(articles)} raw articles fed into the pipeline.")
            for i, article in enumerate(articles):
                with st.container(border=True):
                    st.markdown(f"**{i+1}. [{article.get('source', {}).get('name', 'Unknown')}] {article.get('title')}**")
                    st.caption(article.get('description', 'No description.'))
                    if article.get('url'):
                        st.markdown(f"[Read full article ↗]({article.get('url')})")

    else:
        st.info("👈 Select a sector in the sidebar and click **Run Hybrid Analysis** to begin.")

if __name__ == "__main__":
    main()