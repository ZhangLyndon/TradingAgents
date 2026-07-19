from typing import Annotated

import pandas_ta_classic  # noqa
import yfinance as yf
from langchain_core.tools import tool


@tool
def get_technical_analysis(ticker: Annotated[str, "Yahoo Finance symbol"],
                           period: Annotated[str, "Lookback period"] = "3mo",
                           interval: Annotated[str, "Data frequency"] = "1d") -> str:
    """
    Compute technical analysis indicators for a stock ticker over a specified time
    period and candle (sampling + aggregation) interval. Returns a summary string
    of the computed indicators.
    """
    # Fetch historical market data (OHLCV candles) for the requested lookback
    # period and candle interval
    stock = yf.Ticker(ticker)
    df = stock.history(period = period, interval = interval)

    # Return an error message if insufficient market data was found
    if len(df) < 2:
        return f"Error: Insufficient market data for ticker {ticker}."

    # Calculate technical analysis indicators (relative strength index, moving
    # average convergence / divergence, simple moving average over the past 20
    # and 50 candles / rows), and append them as new columns to the market data
    # DataFrame.
    df.ta.rsi(append = True)
    df.ta.macd(append = True)
    df.ta.sma(length = 20, append = True)
    df.ta.sma(length = 50, append = True)

    # Extract the final 2 candles from the market data
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # Format a concise numerical technical profile for the LLM
    summary = f"""
    Technical Analysis Profile for {ticker} ({interval} candles, {period} lookback):
    - Current Price: ${latest["Close"]:.2f}
    - 20-candle Simple Moving Average (SMA): ${latest["SMA_20"]:.2f}
    - 50-candle Simple Moving Average (SMA): ${latest["SMA_50"]:.2f}
    - Relative Strength Index (RSI): {latest["RSI_14"]:.2f}
    - MACD Line: {latest["MACD_12_26_9"]:.4f}
    - MACD Signal Line: {latest["MACDs_12_26_9"]:.4f}
    - Price Trend: {"UP" if latest["Close"] > previous["Close"] else "DOWN"}
    """
    return summary
