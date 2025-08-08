from datetime import datetime
import time

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf

def fetch_close_series(ticker, period='5y', interval='1d'):
    """
    Fetches a pandas Series of daily Close prices for the given ticker.
    """
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    return df['Close']

def plot_smas(ticker, sma_windows=[50, 100, 200]):
    series = fetch_close_series(ticker)
    if series is None or series.empty:
        print(f"[{ticker}] no data returned, skipping.")
        return

    # Sanity check lengths
    print(f"[{ticker}] bars: {len(series)}", end='')
    for w in sma_windows:
        sma = series.rolling(window=w).mean()
        print(f" | SMA{w}: {len(sma)}", end='')
    print()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(series.index, series.values,
            color='black', linewidth=1, label='Close')

    for w in sma_windows:
        sma = series.rolling(window=w).mean()
        ax.plot(sma.index, sma.values,
                label=f'{w}-Day SMA',
                linewidth=1.5)

    ax.set_title(f'{ticker} — Close Price & SMAs')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend(loc='upper left')
    fig.tight_layout()

    filename = f'{ticker}_sma.png'
    fig.savefig(filename)
    plt.close(fig)
    print(f"Saved {filename}")

if __name__ == '__main__':
    tickers = [
        # Original 50 tickers
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "TSLA", "META", "UNH", "JPM", "JNJ",
        "V", "PG", "MA", "HD", "BAC", "XOM", "PFE", "CVX", "KO", "MRK",
        "ABBV", "VZ", "T", "WMT", "DIS", "NKE", "INTC", "ORCL", "CRM", "MCD",
        "ABT", "CSCO", "PEP", "NFLX", "TMUS", "COST", "MDT", "LLY", "TXN", "AVGO",
        "WFC", "UPS", "QCOM", "HON", "DHR", "ACN", "AMD", "PYPL", "NEE", "SBUX",
        "ADBE", "ADP", "ANTM", "ANET", "APD", "ATVI", "AVB", "BK", "BLK", "BXP",
        "CCI", "CHTR", "CL", "CMCSA", "COF", "COP", "CSX", "DD", "DHI", "DUK",
        "DOW", "DLR", "FDX", "GIS", "GM", "GS", "GOOG", "HLT", "HPE", "HSY",
        "IBM", "ICE", "JCI", "KHC", "KMI", "LMT", "LRCX", "LULU", "MAR", "MCO",
        "MDLZ", "MET", "MMM", "MO", "MS", "MSI", "NOC", "NXPI", "O", "ORLY",
        "PAYX", "PGR", "PLD", "PRU", "PXD", "REGN", "RF", "RTX", "SCHW", "SHW",
        "SLB", "SNAP", "SO", "SPGI", "STZ", "TGT", "TJX", "TRV", "UNP", "USB",
        "VLO", "VRTX", "WBA", "WMB", "XEL", "XLNX", "ZTS", "SYK", "TROW", "URBN",
        "VFC", "WEC", "YUM", "ZBH", "ZBRA", "AON", "AIG", "AFL", "AEP", "AMT",
        "AXP", "BA", "CAT", "ECL", "EMR", "ETN", "HCA", "KMB", "LIN", "PWR",
        "AAL", "ADI", "ALGN", "ALXN", "AMGN", "AMCR", "APTV", "APA", "ARE", "BAX",
        "BBY", "BDX", "BIIB", "BKNG", "BMY", "BSX", "CAG", "CARR", "CB", "CDNS",
        "CDW", "CERN", "CF", "CHD", "CMI", "CMA", "CMS", "CNC", "CPB", "CTAS",
        "CTLT", "CTSH", "CVS", "CZR", "DFS", "DG", "DGX", "ETR", "EXC", "F",
        "FIS", "FISV", "FITB", "FL", "FLEX", "GD", "GILD", "GLW", "HAL", "HAS",
        "HES", "HIG", "HRL", "HST", "HUM", "INFO", "IQV", "IP", "IR", "IPG",
        "JNPR", "JBHT", "KDP", "KLAC", "KSS", "KEY", "KSU", "LHX", "LKQ", "LOW",
        "LUV", "LYB", "MAA", "MAS", "MMC", "MNST", "MOS", "MPC", "MRNA", "MTB",
        "MU", "MXIM", "NCLH", "NEM", "NLY", "NTRS", "NUE", "NWSA", "ODFL", "OMC",
        "OXY", "PAYC", "PBCT", "PNC", "PPL", "PVH", "QRVO", "RCL", "RL", "ROP"
    ]
    for ticker in tickers:
        plot_smas(ticker)