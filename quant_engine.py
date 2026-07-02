import yfinance as yf
import pandas as pd
import numpy as np
import ta
from typing import Optional, Dict, Any


class QuantEngine:
    """Institutional-grade quantitative analysis engine for equity research."""
    
    def get_deep_analysis(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1y", interval="1d")
            if hist.empty or len(hist) < 2:
                return None
            data_quality_warning = None
            if len(hist) < 200:
                data_quality_warning = f"Limited data: only {len(hist)} days available (200 recommended)"
            info = ticker.info
            if not info:
                return None
            current_price = hist['Close'].iloc[-1]
            value_metrics = self._calculate_value_metrics(info, current_price, hist)
            momentum_metrics = self._calculate_momentum_metrics(info, current_price, hist)
            quality_metrics = self._calculate_quality_metrics(info, current_price, hist)
            size_metrics = self._calculate_size_metrics(info, current_price, hist)
            volatility_metrics = self._calculate_volatility_metrics(info, current_price, hist)
            risk_adjusted_metrics = self._calculate_risk_adjusted_metrics(hist['Close'])
            technical_summary = self._calculate_technical_summary(current_price, hist)
            result = {
                "symbol": ticker_symbol,
                "current_price": round(current_price, 2),
                "market_cap": info.get('marketCap'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "value": value_metrics,
                "momentum": momentum_metrics,
                "quality": quality_metrics,
                "size": size_metrics,
                "volatility": volatility_metrics,
                "risk_adjusted": risk_adjusted_metrics,
                "technical_summary": technical_summary,
            }
            total_score = sum([value_metrics.get('score', 0), momentum_metrics.get('score', 0), quality_metrics.get('score', 0), size_metrics.get('score', 0), volatility_metrics.get('score', 0)])
            result["total_factor_score"] = total_score
            result["normalized_score"] = round((total_score / 59) * 100, 1)
            if data_quality_warning:
                result["data_quality_warning"] = data_quality_warning
            return result
        except Exception as e:
            print(f"Quant Engine failed for {ticker_symbol}: {e}")
            return None
    
    def _calculate_value_metrics(self, info, current_price, hist):
        pe_ratio = info.get('trailingPE')
        forward_pe = info.get('forwardPE')
        peg_ratio = info.get('pegRatio')
        ps_ratio = info.get('priceToSalesTrailing12Months')
        pb_ratio = info.get('priceToBook')
        ev_ebitda = info.get('enterpriseToEbitda')
        fcf = info.get('freeCashflow')
        shares_outstanding = info.get('sharesOutstanding')
        fcf_yield = None
        if fcf and shares_outstanding and current_price > 0:
            fcf_per_share = fcf / shares_outstanding
            fcf_yield = (fcf_per_share / current_price) * 100
        score = 0
        if pe_ratio is not None:
            if pe_ratio < 15: score += 3
            elif pe_ratio < 25: score += 1
        if peg_ratio is not None:
            if peg_ratio < 1: score += 4
            elif peg_ratio < 1.5: score += 2
        if fcf_yield is not None:
            if fcf_yield > 8: score += 4
            elif fcf_yield >= 5: score += 2
        if ev_ebitda is not None:
            if ev_ebitda < 10: score += 2
            elif ev_ebitda < 20: score += 1
        if pb_ratio is not None:
            if pb_ratio < 1.5: score += 2
            elif pb_ratio < 3: score += 1
        return {"pe_ratio": round(pe_ratio, 2) if pe_ratio else None, "forward_pe": round(forward_pe, 2) if forward_pe else None, "peg_ratio": round(peg_ratio, 2) if peg_ratio else None, "ps_ratio": round(ps_ratio, 2) if ps_ratio else None, "pb_ratio": round(pb_ratio, 2) if pb_ratio else None, "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None, "fcf_yield": round(fcf_yield, 2) if fcf_yield else None, "score": score}
    
    def _calculate_momentum_metrics(self, info, current_price, hist):
        close_prices = hist['Close']
        rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi().iloc[-1]
        macd_ind = ta.trend.MACD(close=close_prices)
        macd_line = macd_ind.macd().iloc[-1]
        macd_signal = macd_ind.macd_signal().iloc[-1]
        macd_histogram = macd_line - macd_signal
        sma_50 = ta.trend.SMAIndicator(close=close_prices, window=50).sma_indicator().iloc[-1]
        sma_200 = ta.trend.SMAIndicator(close=close_prices, window=200).sma_indicator().iloc[-1]
        price_vs_sma50 = current_price / sma_50 if sma_50 else None
        price_vs_sma200 = current_price / sma_200 if sma_200 else None
        high_52w = hist['High'].max()
        proximity_to_52w_high = current_price / high_52w if high_52w else None
        roc_20d = None
        if len(hist) >= 20:
            price_20d_ago = hist['Close'].iloc[-20]
            if price_20d_ago:
                roc_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
        score = 0
        if rsi is not None:
            if 40 <= rsi <= 60: score += 2
            elif rsi < 30: score += 3
            elif rsi > 70: score = max(0, score - 1)
        if macd_histogram is not None and macd_histogram > 0: score += 2
        if price_vs_sma50 and current_price > sma_50: score += 2
        if price_vs_sma200 and current_price > sma_200: score += 2
        if proximity_to_52w_high:
            if proximity_to_52w_high > 0.9: score += 2
            elif proximity_to_52w_high > 0.7: score += 1
        if roc_20d is not None:
            if roc_20d > 5: score += 2
            elif roc_20d > 0: score += 1
        return {"rsi_14": round(rsi, 2) if rsi is not None else None, "macd_line": round(macd_line, 4) if macd_line is not None else None, "macd_signal": round(macd_signal, 4) if macd_signal is not None else None, "macd_histogram": round(macd_histogram, 4) if macd_histogram is not None else None, "price_vs_sma50": round(price_vs_sma50, 3) if price_vs_sma50 else None, "price_vs_sma200": round(price_vs_sma200, 3) if price_vs_sma200 else None, "proximity_to_52w_high": round(proximity_to_52w_high, 3) if proximity_to_52w_high else None, "roc_20d": round(roc_20d, 2) if roc_20d else None, "score": score}
    
    def _calculate_quality_metrics(self, info, current_price, hist):
        roe = info.get('returnOnEquity')
        roe_pct = roe * 100 if roe else None
        operating_income = info.get('operatingIncome')
        tax_rate = info.get('taxRate')
        total_equity = info.get('totalStockholderEquity')
        total_debt = info.get('totalDebt')
        cash = info.get('cash') or info.get('cashAndCashEquivalents')
        roic_pct = None
        if operating_income and total_equity and total_debt:
            effective_tax = tax_rate if tax_rate else 0.21
            nopat = operating_income * (1 - effective_tax)
            invested_capital = total_equity + total_debt - (cash if cash else 0)
            if invested_capital > 0:
                roic_pct = (nopat / invested_capital) * 100
        gross_profits = info.get('grossProfits')
        total_assets = info.get('totalAssets')
        gross_profitability_pct = None
        if gross_profits and total_assets and total_assets > 0:
            gross_profitability_pct = (gross_profits / total_assets) * 100
        debt_to_equity = info.get('debtToEquity')
        if debt_to_equity and debt_to_equity > 10:
            debt_to_equity = debt_to_equity / 100
        ebitda = info.get('ebitda')
        interest_expense = info.get('interestExpense')
        interest_coverage = None
        if ebitda and interest_expense and interest_expense > 0:
            interest_coverage = ebitda / interest_expense
        current_assets = info.get('totalCurrentAssets')
        current_liabilities = info.get('totalCurrentLiabilities')
        current_ratio = None
        if current_assets and current_liabilities and current_liabilities > 0:
            current_ratio = current_assets / current_liabilities
        operating_margin = info.get('operatingMargins')
        operating_margin_pct = operating_margin * 100 if operating_margin else None
        score = 0
        if roe_pct is not None:
            if roe_pct > 15: score += 3
            elif roe_pct >= 10: score += 2
        if roic_pct is not None:
            if roic_pct > 12: score += 3
            elif roic_pct >= 8: score += 2
        if gross_profitability_pct is not None:
            if gross_profitability_pct > 40: score += 3
            elif gross_profitability_pct >= 25: score += 2
        if debt_to_equity is not None:
            if debt_to_equity < 0.5: score += 3
            elif debt_to_equity <= 1.0: score += 1
            else: score = max(0, score - 1)
        if current_ratio is not None:
            if current_ratio > 1.5: score += 3
            elif current_ratio >= 1.0: score += 1
            else: score = max(0, score - 2)
        if operating_margin_pct is not None:
            if operating_margin_pct > 20: score += 3
            elif operating_margin_pct >= 10: score += 1
        return {"roe": round(roe_pct, 2) if roe_pct else None, "roic": round(roic_pct, 2) if roic_pct else None, "gross_profitability": round(gross_profitability_pct, 2) if gross_profitability_pct else None, "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity else None, "interest_coverage": round(interest_coverage, 2) if interest_coverage else None, "current_ratio": round(current_ratio, 2) if current_ratio else None, "operating_margin": round(operating_margin_pct, 2) if operating_margin_pct else None, "score": score}
    
    def _calculate_size_metrics(self, info, current_price, hist):
        market_cap = info.get('marketCap')
        if market_cap is None:
            market_cap_category = "N/A"
        elif market_cap < 2e9:
            market_cap_category = "Small"
        elif market_cap <= 10e9:
            market_cap_category = "Mid"
        else:
            market_cap_category = "Large"
        revenue_growth = info.get('revenueGrowth')
        revenue_growth_pct = revenue_growth * 100 if revenue_growth else None
        score = 0
        if market_cap is not None:
            if market_cap < 2e9: score += 3
            elif market_cap <= 10e9: score += 2
        if revenue_growth_pct is not None:
            if revenue_growth_pct > 20: score += 2
            elif revenue_growth_pct >= 10: score += 1
        return {"market_cap": market_cap, "market_cap_category": market_cap_category, "revenue_growth": round(revenue_growth_pct, 2) if revenue_growth_pct else None, "score": score}
    
    def _calculate_volatility_metrics(self, info, current_price, hist):
        close_prices = hist['Close']
        beta = info.get('beta')
        bb = ta.volatility.BollingerBands(close=close_prices, window=20, window_dev=2)
        bb_upper = bb.bollinger_hband().iloc[-1]
        bb_lower = bb.bollinger_lband().iloc[-1]
        bollinger_width = ((bb_upper - bb_lower) / current_price) * 100 if current_price else None
        if len(hist) >= 30:
            log_returns = np.log(close_prices / close_prices.shift(1))
            hist_vol_30d = log_returns.iloc[-30:].std() * np.sqrt(252) * 100
        else:
            log_returns = np.log(close_prices / close_prices.shift(1))
            hist_vol_30d = log_returns.std() * np.sqrt(252) * 100
        max_drawdown = self._calculate_max_drawdown(close_prices)
        score = 0
        if beta is not None:
            if beta < 0.8: score += 3
            elif beta <= 1.2: score += 1
            else: score = max(0, score - 1)
        if bollinger_width is not None:
            if bollinger_width < 10: score += 3
            elif bollinger_width <= 20: score += 1
        if max_drawdown is not None:
            if max_drawdown < 15: score += 3
            elif max_drawdown <= 25: score += 1
            else: score = max(0, score - 1)
        return {"beta": round(beta, 2) if beta else None, "bollinger_width": round(bollinger_width, 2) if bollinger_width else None, "historical_vol_30d": round(hist_vol_30d, 2) if hist_vol_30d else None, "max_drawdown_1y": round(max_drawdown, 2) if max_drawdown else None, "score": score}
    
    def _calculate_risk_adjusted_metrics(self, price_series):
        risk_free_rate = 0.04
        daily_returns = price_series.pct_change().dropna()
        if len(daily_returns) < 2:
            return {"sharpe_ratio": None, "sortino_ratio": None, "calmar_ratio": None}
        total_return = (price_series.iloc[-1] / price_series.iloc[0]) - 1
        num_years = len(price_series) / 252
        annualized_return = (1 + total_return) ** (1 / num_years) - 1 if num_years > 0 else total_return
        annualized_std = daily_returns.std() * np.sqrt(252)
        sharpe_ratio = None
        if annualized_std and annualized_std > 0:
            sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        sortino_ratio = None
        negative_returns = daily_returns[daily_returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std() * np.sqrt(252)
            if downside_deviation > 0:
                sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation
        calmar_ratio = None
        max_drawdown = self._calculate_max_drawdown(price_series)
        if max_drawdown is not None and max_drawdown > 0:
            calmar_ratio = annualized_return / (max_drawdown / 100)
        return {"sharpe_ratio": round(sharpe_ratio, 2) if sharpe_ratio else None, "sortino_ratio": round(sortino_ratio, 2) if sortino_ratio else None, "calmar_ratio": round(calmar_ratio, 2) if calmar_ratio else None}
    
    def _calculate_max_drawdown(self, price_series):
        if len(price_series) < 2:
            return None
        running_max = price_series.cummax()
        drawdown = (running_max - price_series) / running_max * 100
        max_dd = drawdown.max()
        return max_dd if max_dd > 0 else 0.0
    
    def _calculate_technical_summary(self, current_price, hist):
        close_prices = hist['Close']
        sma_50 = ta.trend.SMAIndicator(close=close_prices, window=50).sma_indicator().iloc[-1]
        sma_200 = ta.trend.SMAIndicator(close=close_prices, window=200).sma_indicator().iloc[-1]
        if current_price > sma_50 > sma_200:
            trend = "Bullish"
        elif current_price < sma_50 < sma_200:
            trend = "Bearish"
        else:
            trend = "Neutral"
        if sma_50 and current_price:
            price_vs_sma50_pct = ((current_price - sma_50) / sma_50) * 100
            if price_vs_sma50_pct > 5 and sma_50 > sma_200:
                trend_strength = "Strong"
            elif abs(price_vs_sma50_pct) <= 2:
                trend_strength = "Weak"
            else:
                trend_strength = "Moderate"
        else:
            trend_strength = "Moderate"
        return {"trend": trend, "trend_strength": trend_strength}


if __name__ == "__main__":
    engine = QuantEngine()
    result = engine.get_deep_analysis("AAPL")
    if result:
        import json
        print(json.dumps(result, indent=2))
    else:
        print("Analysis failed for AAPL")
