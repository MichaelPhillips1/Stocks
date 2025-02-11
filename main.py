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

tickers = ["HL", "AMZN", "AAPL", "NFLX", "NVDA", "PLTR"]
CurrentDate = datetime.date.today()
PreviousDate = CurrentDate - datetime.timedelta(days=7 * 35)

for ticker in tickers:
    try:
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = ParseData(request)
    except:
        time.sleep(15)
        continue

    while True:
        try:
            currentPrice = float(input(f"Please enter the current days price for {ticker}: "))
            currentData = data[1]
            currentData.append(currentPrice)
            break
        except:
            continue

    period=14
    rsi = CalculateRSI(currentData, period)

    fig, axs = plt.subplots(2, 1, figsize=(10, 8))
    axs[0].plot([i for i in range(len(data[1]))], data[1])
    axs[0].set_xlabel("Time Scale (Days)")
    axs[0].set_ylabel("Price")

    axs[1].plot([i + period + 1 for i in range(len(rsi))], rsi)
    axs[1].set_xlabel("Time Scale (Days)")
    axs[1].set_ylabel("RSI")

    axs[1].axhline(70, color='red', linestyle='--', label='Threshold 70')
    axs[1].axhline(30, color='green', linestyle='--', label='Threshold 30')
    axs[1].fill_between([i + period + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
    axs[1].fill_between([i + period + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)

    plt.savefig(f"Charts/{ticker}_{CurrentDate}.png")
    time.sleep(15)