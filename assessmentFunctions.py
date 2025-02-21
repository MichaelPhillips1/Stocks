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