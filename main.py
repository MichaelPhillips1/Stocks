import time
from itertools import accumulate

import requests
from datetime import date, timedelta
import statistics

def ParseData(results):
    dates = [result['t'] for result in results]
    closing_prices = [result['c'] for result in results]
    high_prices = [result['h'] for result in results]
    low_prices = [result['l'] for result in results]
    open_prices = [result['o'] for result in results]
    dates = [str(date.fromtimestamp(d / 1000)) for d in dates]

    return [dates, closing_prices, open_prices, high_prices, low_prices]

def LogAndOutput(information, file):
    file.write(information + "\n")
    print(information)

def CalculateRSI(data):
    closing_prices = data[1][-(15 + 1):]
    price_changes = [closing_prices[i] - closing_prices[i - 1] for i in range(1, len(closing_prices))]

    gains = [change if change > 0 else 0 for change in price_changes]
    losses = [-change if change < 0 else 0 for change in price_changes]

    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14
    for i in range(14, len(price_changes)):
        avg_gain = ((avg_gain * (14 - 1)) + gains[i]) / 14
        avg_loss = ((avg_loss * (14 - 1)) + losses[i]) / 14

    if avg_loss == 0:
        rs = 100
    else:
        rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def CalculateMACD(data):
    def ema(prices, period):
        ema_values = [prices[0]]
        alpha = 2 / (period + 1)
        for price in prices[1:]:
            ema_values.append((price * alpha) + (ema_values[-1] * (1 - alpha)))
        return ema_values

    short_ema = ema(data[1], 12)
    long_ema = ema(data[1], 26)

    macd_line = [s - l for s, l in zip(short_ema, long_ema)]
    signal_line = ema(macd_line, 9)

    return macd_line, signal_line


def calculate_bollinger_bands(data, window_size=20, num_std_dev=2):

    moving_avg = []
    upper_band = []
    lower_band = []

    for i in range(len(data[1]) - window_size + 1):
        window = data[1][i:i + window_size]
        avg = sum(window) / window_size
        std_dev = statistics.stdev(window)

        moving_avg.append(avg)
        upper_band.append(avg + num_std_dev * std_dev)
        lower_band.append(avg - num_std_dev * std_dev)

    upper_lower_distance = []

    for i, element in enumerate(upper_band):
        upper_lower_distance.append(element - lower_band[i])

    avg_upper_lower_distance = sum(upper_lower_distance) / len(upper_band)

    print(upper_lower_distance)
    print(avg_upper_lower_distance)

    return moving_avg, upper_band, lower_band, upper_lower_distance, avg_upper_lower_distance

def PrintRSI(Ticker, rsi, file):
    if(rsi <= 35):
        LogAndOutput(f"(+) {Ticker} is a buy, with an rsi <= 35 at {rsi}.", file)
    elif(rsi >= 65):
        LogAndOutput(f"(-) {Ticker} is a sell, with an rsi >= 65 at {rsi}.", file)
    else:
        LogAndOutput(f"(?) {Ticker} could be trending either direction, with an rsi of {rsi}.", file)

def PrintMACD(Ticker, macd, macdsignal, file):
    if(macd[-2] < macdsignal[-2] and macd[-1] > macdsignal[-1]):
        LogAndOutput(f"(+) {Ticker} is a buy, with MACD crossing above, signaling buy.", file)
    elif(macd[-2] > macdsignal[-2] and macd[-1] < macdsignal[-1]):
        LogAndOutput(f"(-) {Ticker} is a sell, with MACD crossing below, signaling sell.", file)
    if(macd[-1] < macdsignal[-1]):
        LogAndOutput(f"(-) {Ticker} MACD remains below signal by {macdsignal[-1] - macd[-1]} with a slope of {(macd[-1] - macd[-2])/2}.", file)
    else:
        LogAndOutput(f"(+) {Ticker} MACD remains above signal by {macd[-1] - macdsignal[-1]} with a slope of {(macd[-1] - macd[-2]) / 2}.", file)

TickerList = ["AAPL", "MSFT", "TSLA", "GOOGL", "NVDA", "META", "IBM", "NFLX", "AVGO", "UBER"]
CurrentDate = date.today()
PreviousDate = CurrentDate - timedelta(days=100)
file = open(f"{CurrentDate.isoformat()}.txt", "w")
LogAndOutput("*" * 200, file)

for i, Ticker in enumerate(TickerList):
    try:
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{Ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC")
        results = request.json()['results'][-53:]
    except:
        continue

    data = ParseData(results)
    rsi = CalculateRSI(data)
    macd, macdsignal = CalculateMACD(data)
    bollinger_moving_avg, bollinger_upper_band, bollinger_lower_band, bollinger_upper_lower_distance, bollinger_avg_upper_lower_distance = calculate_bollinger_bands(data)

    PrintRSI(Ticker, rsi, file)
    PrintMACD(Ticker, macd, macdsignal, file)
    LogAndOutput("*"*200, file)

    if(i != len(TickerList)-1):
        time.sleep(15)

file.close()