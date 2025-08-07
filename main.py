from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf

def fetch_daily_ohlcv_lists(ticker, period='5y', interval='1d'):
    """
    Fetches the last N years of daily OHLCV data for a given ticker from yfinance and returns it as lists.
    """
    ticker_obj = yf.Ticker(ticker)
    hist = ticker_obj.history(period=period, interval=interval)

    dates  = [dt.strftime('%Y-%m-%d') for dt in hist.index]
    opens  = hist['Open'].tolist()
    highs  = hist['High'].tolist()
    lows   = hist['Low'].tolist()
    closes = hist['Close'].tolist()
    vols   = hist['Volume'].tolist()

    return dates, opens, highs, lows, closes, vols

def compute_ema(values, length):
    """
    Computes an exponential moving average of given length over `values`.
    """
    k = 2 / (length + 1)
    ema = []
    for i, v in enumerate(values):
        if i == 0:
            ema.append(v)
        else:
            ema.append(v * k + ema[-1] * (1 - k))
    return ema

def find_cross_points(closes, ema):
    """
    Finds indices where the price crosses the EMA.
    A cross is detected when (close - ema) changes sign from one bar to the next.
    """
    crosses = []
    diffs = np.array(closes) - np.array(ema)
    for i in range(1, len(diffs)):
        if diffs[i] * diffs[i-1] < 0:
            crosses.append(i)
    return crosses

if __name__ == '__main__':
    # list of tickers to process
    tickers = [
        # Original 50 tickers
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "TSLA", "META", "UNH", "JPM", "JNJ",
        "V", "PG", "MA", "HD", "BAC", "XOM", "PFE", "CVX", "KO", "MRK",
        "ABBV", "VZ", "T", "WMT", "DIS", "NKE", "INTC", "ORCL", "CRM", "MCD",
        "ABT", "CSCO", "PEP", "NFLX", "TMUS", "COST", "MDT", "LLY", "TXN", "AVGO",
        "WFC", "UPS", "QCOM", "HON", "DHR", "ACN", "AMD", "PYPL", "NEE", "SBUX",

        # Additional 100 tickers
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
    ]
    ema_lengths = [50, 100, 200]  # EMA periods
    bb_length = 20               # Bollinger Bands moving average period
    bb_std_dev = 2               # number of standard deviations

    # color palette
    cmap = plt.get_cmap('tab10')

    for ticker in tickers:
        # fetch price data
        dates, opens, highs, lows, closes, volumes = fetch_daily_ohlcv_lists(ticker)
        x_dates = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

        # compute Bollinger Bands
        df = pd.DataFrame({'Close': closes})
        df['MiddleBand'] = df['Close'].rolling(window=bb_length).mean()
        df['Std'] = df['Close'].rolling(window=bb_length).std()
        df['UpperBand'] = df['MiddleBand'] + bb_std_dev * df['Std']
        df['LowerBand'] = df['MiddleBand'] - bb_std_dev * df['Std']
        middle = df['MiddleBand'].tolist()
        upper = df['UpperBand'].tolist()
        lower = df['LowerBand'].tolist()

        # setup figure
        plt.figure(figsize=(12, 6))
        plt.plot(x_dates, closes, color='black', linewidth=1, label='Close Price', zorder=1)

        # plot Bollinger Bands
        # plt.plot(x_dates, middle, label=f'{bb_length}-Period SMA (BB)', linestyle='-', linewidth=1, zorder=1)
        plt.plot(x_dates, upper, label='Upper Bollinger Band', color='purple', linestyle='--', linewidth=1, zorder=1)
        plt.plot(x_dates, lower, label='Lower Bollinger Band', color='purple', linestyle='--', linewidth=1, zorder=1)

        # plot each EMA and its crossover points
        for idx, length in enumerate(ema_lengths):
            ema = compute_ema(closes, length)
            crosses = find_cross_points(closes, ema)
            color = cmap(idx % cmap.N)

            # EMA line
            plt.plot(x_dates, ema, label=f'{length}-Period EMA', color=color, zorder=2)

            # crossover dots
            cross_dates = [x_dates[i] for i in crosses]
            cross_vals  = [closes[i]    for i in crosses]
            plt.scatter(cross_dates, cross_vals, marker='o', s=10, color=color, zorder=3)

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'{ticker} Price with EMAs, Cross Points, and Bollinger Bands')
        plt.legend(loc='upper left')
        plt.tight_layout()

        # save to file
        filename = f'{ticker}.png'
        plt.savefig(filename)
        print(f"Chart saved to {filename}")

        # close the figure to free memory
        plt.close()
