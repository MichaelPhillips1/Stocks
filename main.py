import time
import requests
import datetime
import matplotlib.pyplot as plt
plt.switch_backend('TkAgg')

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

while True:
    CurrentDate = datetime.date.today()
    PreviousDate = CurrentDate - datetime.timedelta(days=7*52*2)
    try:
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/X:BTCUSD/range/1/week/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = ParseData(request)
    except:
        time.sleep(15)
        continue

    period = 14
    rsi = CalculateRSI(data[1], period)

    formatted_times = [
        datetime.datetime.fromtimestamp(ts / 1000).strftime('%m/%d/%Y %H:%M') for ts in data[0]
    ]
    for i in range(len(rsi)):
        print(f"Time: {formatted_times[(-len(rsi)):][i]}, Price: {data[1][(-len(rsi)):][i]}, RSI: {rsi[(-len(rsi)) + i]}")

    #According to sales rep, without premium memebrhsip you are limited to x queries per minute, with only previous trading day data available.
    #Once a membership is purchased however, there are endless queries per minute, with finer scopes such as 1 minute being allowed, and best of all
    #You are able to get the CURRENT market data, so the query in this code for 1 hour would return the hour of for THIS trading day, the final
    #Trading hour for yesterday

    print(datetime.datetime.fromtimestamp(data[0][-1] / 1000).strftime('%m/%d/%Y %H:%M'), "Latest time stamp")

    fig, axs = plt.subplots(2, 1)
    axs[0].plot(([i+1 for i in range(len(rsi))]), data[1][period + 1:])
    axs[0].xlabel("Week")
    axs[0].ylabel("Price")
    axs[1].plot(([i+1 for i in range(len(rsi))]), rsi, marker='o', linestyle='-', color='b', label='RSI')
    axs[1].xlabel("Week")
    axs[1].ylabel("RSI")
    plt.show()
    time.sleep(15)