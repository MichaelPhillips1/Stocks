import datetime, requests

def formPolygonQuery(ticker):
    CurrentDate = datetime.date.today()
    PreviousDate = CurrentDate - datetime.timedelta(days=7 * 52)
    return requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']

def parseDataPolygon(results):
    dates = [result['t'] for result in results]
    closing_prices = [result['c'] for result in results]
    high_prices = [result['h'] for result in results]
    low_prices = [result['l'] for result in results]
    open_prices = [result['o'] for result in results]
    volume = [result['v'] for result in results]

    return [dates, closing_prices, open_prices, high_prices, low_prices, volume]

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

def calculateFibonacciRetracements(price_array):
    if not price_array:
        return []
    
    trend = -1
    if price_array[-1] > price_array[0]:
        trend = 1
    
    high = max(price_array)
    low = min(price_array)
    diff = high - low

    if trend == 1:
        return [high, high - 0.236 * diff, high - 0.382 * diff, high - 0.500 * diff, high - 0.618 * diff, high - 0.786 * diff, low]
    else:
        return [low, low + 0.236 * diff, low + 0.382 * diff, low + 0.500 * diff, low + 0.618 * diff, low + 0.786 * diff, high]

def calculateWilliamsR(high_prices, low_prices, close_prices, period=14):
    williams_r = []
    for i in range(period - 1, len(close_prices)):
        window_highs = high_prices[i - period + 1 : i + 1]
        window_lows = low_prices[i - period + 1 : i + 1]
        highest_high = max(window_highs)
        lowest_low = min(window_lows)
        current_close = close_prices[i]
        if highest_high - lowest_low == 0:
            wr = 0
        else:
            wr = (highest_high - current_close) / (highest_high - lowest_low) * -100
        williams_r.append(wr)
    return williams_r