import time
import requests
import datetime
import matplotlib.pyplot as plt
plt.switch_backend('TkAgg')
plt.style.use('dark_background')

def ParseData(results):
    dates = [result['t'] for result in results]
    closing_prices = [result['c'] for result in results]
    high_prices = [result['h'] for result in results]
    low_prices = [result['l'] for result in results]
    open_prices = [result['o'] for result in results]

    return [dates, closing_prices, open_prices, high_prices, low_prices]

def CalculateRSI(closing_prices, period = 14):
    totalRSI = []
    price_changes = [closing_prices[i] - closing_prices[i - 1] for i in range(1, len(closing_prices))]
    gains = [max(change, 0) for change in price_changes]
    losses = [-min(change, 0) for change in price_changes]
    alpha = 1 / period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(closing_prices) - 1):
        current_gain = gains[i]
        current_loss = losses[i]
        avg_gain = (alpha * current_gain) + ((1 - alpha) * avg_gain)
        avg_loss = (alpha * current_loss) + ((1 - alpha) * avg_loss)
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        totalRSI.append(100 - (100 / (1 + rs)))
    return totalRSI

def calculateBollingerBands(prices, period=14, num_std_dev=2):
    rolling_mean = []
    rolling_std = []
    for i in range(len(prices) - period + 1):
        window_prices = prices[i:i + period]
        mean = sum(window_prices) / period
        std_dev = (sum((p - mean) ** 2 for p in window_prices) / (period - 1)) ** 0.5  # Sample std dev
        rolling_mean.append(mean)
        rolling_std.append(std_dev)
    upper_band = [m + (num_std_dev * s) for m, s in zip(rolling_mean, rolling_std)]
    lower_band = [m - (num_std_dev * s) for m, s in zip(rolling_mean, rolling_std)]
    return [rolling_mean, upper_band, lower_band]

tickers = ["MSFT", "HL", "AMZN", "AAPL", "NFLX", "NVDA", "PLTR", "GOOGL", "META", "TSLA", "JNJ", "JPM", "V", "DIS", "PFE", "CSCO", "XOM", "T", "WMT"]
CurrentDate = datetime.date.today()
PreviousDate = CurrentDate - datetime.timedelta(days=7 * 50)
for ind, ticker in enumerate(tickers):
    try:
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/week/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = ParseData(request)
        currentPriceData = data[1]
        print(currentPriceData[-1])
    except:
        time.sleep(15)
        continue

    # Set parameters for indicators
    periodRSI = 14
    periodBollinger = 14
    stdDevBollinger = 2

    # Calculate indicators
    rsi = CalculateRSI(currentPriceData, periodRSI)
    bollinger = calculateBollingerBands(currentPriceData, periodBollinger, stdDevBollinger)

    # Figure for plots
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    # Plot stock prices
    axs[0].plot([i for i in range(len(currentPriceData))], currentPriceData)
    # Plot bollingers over the prices
    axs[0].plot([i + periodBollinger - 1 for i in range(len(bollinger[0]))], bollinger[0], color='green')
    axs[0].plot([i + periodBollinger - 1 for i in range(len(bollinger[1]))], bollinger[1], color='red')
    axs[0].plot([i + periodBollinger - 1 for i in range(len(bollinger[2]))], bollinger[2], color='red')
    # Set the scale labels of the graph
    axs[0].set_xlabel("Time Scale (Days)")
    axs[0].set_ylabel("Price X Bollinger")

    # Plot the RSI
    axs[1].plot([i + periodRSI + 1 for i in range(len(rsi))], rsi, label=f"RSI: {rsi[-1]}")
    # Set bounds for overbought and oversold
    axs[1].axhline(70, color='red', linestyle='--', label='Threshold 70')
    axs[1].axhline(30, color='green', linestyle='--', label='Threshold 30')
    # Share in areas for overbought and oversold
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)
    # Set the scale labels of the graph
    axs[1].set_xlabel("Time Scale (Days)")
    axs[1].set_ylabel("RSI")

    # Save the graph and wait for next api interval
    plt.savefig(f"./Charts/{ticker}_{CurrentDate}.png")
    time.sleep(15)