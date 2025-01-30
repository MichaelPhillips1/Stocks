import time
import requests
from datetime import date, timedelta

def PrintIchimoku(Ticker, data, file):
    if (data[0] > data[1]):
        LogAndOutput(
            f"(+) {Ticker} is a buy, with Kijunsen(${data[1]}) being ${data[0] - data[1]} below Tenkansen(${data[0]}).", file)
    else:
        LogAndOutput(
            f"(-) {Ticker} is a sell, with Kijunsen(${data[1]}) being ${data[1] - data[0]} above Tenkansen(${data[0]}).", file)

def ParseData(results):
    dates = [result['t'] for result in results]
    closing_prices = [result['c'] for result in results]
    high_prices = [result['h'] for result in results]
    low_prices = [result['l'] for result in results]
    open_prices = [result['o'] for result in results]
    dates = [str(date.fromtimestamp(d / 1000)) for d in dates]

    return [dates, closing_prices, open_prices, high_prices, low_prices]

def CalculateIchimoku(data):

    TenkanSen = (max(data[1][-10:-1]) + min(data[1][-10:-1])) / 2
    KijunSen = (max(data[1][-27:-1]) + min(data[1][-27:-1])) / 2
    ChikouSpan = data[1][-1]
    SenkouSpanA = (TenkanSen + KijunSen) / 2
    SenkouSpanB = (max(data[1]) + min(data[1])) / 2

    return [TenkanSen, KijunSen, ChikouSpan, SenkouSpanA, SenkouSpanB]

def PrintRSI(Ticker, rsi, file):
    if(rsi <= 35):
        LogAndOutput(f"(+) {Ticker} is a buy, with an rsi <= 35 at {rsi}.", file)
    elif(rsi >= 65):
        LogAndOutput(f"(-) {Ticker} is a sell, with an rsi >= 65 at {rsi}.", file)
    else:
        LogAndOutput(f"(?) {Ticker} could be trending either direction, with an rsi of {rsi}.", file)

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

def LogAndOutput(information, file):
    file.write(information + "\n")
    print(information)

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
    ichimoku = CalculateIchimoku(data)
    rsi = CalculateRSI(data)
    macd, macdsignal = CalculateMACD(data)

    PrintIchimoku(Ticker, ichimoku, file)
    PrintRSI(Ticker, rsi, file)
    PrintMACD(Ticker, macd, macdsignal, file)
    LogAndOutput("*"*200, file)

    if(i != len(TickerList)-1):
        time.sleep(15)

file.close()