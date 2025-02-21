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

def calculateRSI(closing_prices, period = 14):
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

def computeEMA(data, period):
    ema = []
    alpha = 2 / (period + 1)
    for i, value in enumerate(data):
        if i == 0:
            ema.append(value)
        else:
            ema.append(alpha * value + (1 - alpha) * ema[i - 1])
    return ema

def calculateMACD(close_prices, fast_period = 12, slow_period = 26, signal_period = 9):
    ema_fast = computeEMA(close_prices, fast_period)
    ema_slow = computeEMA(close_prices, slow_period)
    macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
    signal_line = computeEMA(macd_line, signal_period)
    macd_hist = [macd - signal for macd, signal in zip(macd_line, signal_line)]
    return [signal_line, macd_line, macd_hist]

tickers = ["MSFT", "HL", "AMZN", "AAPL", "NFLX", "NVDA", "PLTR", "GOOGL", "META", "TSLA", "JNJ", "JPM", "V", "DIS", "PFE", "CSCO", "XOM", "T", "WMT", "AVGO", "MA", "ORCL", "BABA", "IBM", "QCOM", "AMD", "SNDL", "TJX", "GFS", "NOK"]
CurrentDate = datetime.date.today()
PreviousDate = CurrentDate - datetime.timedelta(days=7 * 50)
for ind, ticker in enumerate(tickers):
    try:
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = ParseData(request)
        currentPriceData = data[1]
    except:
        time.sleep(15)
        continue

    periodRSI = 14
    periodFastMacd = 12
    periodSlowMacd = 26
    signalPeriodMacd = 9

    rsi = calculateRSI(currentPriceData, periodRSI)
    macd = calculateMACD(currentPriceData, periodFastMacd, periodSlowMacd, signalPeriodMacd)

    fig, axs = plt.subplots(3,1, figsize=(13,13))

    # Plot the price
    axs[0].plot([i for i in range(len(currentPriceData))], currentPriceData, label=f"Price: {currentPriceData[-1]}")
    axs[0].set_xlabel("Time Scale (Days)")
    axs[0].set_ylabel("Price")
    axs[0].legend(loc="upper left")

    # Plot the RSI
    axs[1].plot([i + periodRSI + 1 for i in range(len(rsi))], rsi, label=f"RSI: {rsi[-1]}")
    axs[1].axhline(70, color='red', linestyle='--')
    axs[1].axhline(30, color='green', linestyle='--')
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)
    axs[1].set_xlabel("Time Scale (Days)")
    axs[1].set_ylabel("RSI")
    axs[1].legend(loc="upper left")

    # Plot the MACD
    axs[2].plot([i for i in range(len(macd[0]))], macd[0], color="red", label=f"Signal: {macd[0][-1]}")
    axs[2].plot([i for i in range(len(macd[1]))], macd[1], color="green", label=f"MACD: {macd[1][-1]}")
    axs[2].set_xlabel("Time Scale (Days)")
    axs[2].set_ylabel("MACD")
    axs[2].legend(loc="upper left")

    # Save the graph and wait for next api interval
    plt.savefig(f"./Charts/{ticker}_{CurrentDate}.png")
    time.sleep(15)