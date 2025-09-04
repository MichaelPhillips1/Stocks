import statistics, yfinance as yf
def BollingerBandsPercent(data):
    closes = data["Close"]
    result = []
    for i in range(len(closes)):
        if i < 19:  # need 20 values
            result.append(None)
            continue
        window_slice = closes[i-19:i+1]
        sma = statistics.mean(window_slice)
        stdev = statistics.pstdev(window_slice)
        upper = sma + 2 * stdev
        lower = sma - 2 * stdev
        if upper == lower:
            result.append(None)
        else:
            result.append((closes[i] - lower) / (upper - lower))
    return result


def RSI(data):
    closes = data["Close"]
    result = []
    period = 14

    gains = []
    losses = []

    for i in range(len(closes)):
        if i == 0:
            result.append(None)
            continue

        change = closes[i] - closes[i - 1]
        gain = max(change, 0)
        loss = -min(change, 0)

        gains.append(gain)
        losses.append(loss)

        if i < period:
            result.append(None)
        elif i == period:
            avg_gain = sum(gains) / period
            avg_loss = sum(losses) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
            result.append(100 - (100 / (1 + rs)))
        else:
            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
            result.append(100 - (100 / (1 + rs)))

    return result


def StochRSI(data, rsi):
    period = 14
    smooth_k = 3  # smoothing for %K
    smooth_d = 3  # smoothing for %D

    stoch_rsi = []
    k_values = []
    d_values = []

    # Step 1: compute raw StochRSI
    for i in range(len(rsi)):
        if rsi[i] is None or i < period:
            stoch_rsi.append(None)
            continue

        window = [x for x in rsi[i - period + 1: i + 1] if x is not None]
        if not window:
            stoch_rsi.append(None)
            continue

        min_rsi = min(window)
        max_rsi = max(window)
        if max_rsi == min_rsi:
            stoch_rsi.append(None)
        else:
            stoch_rsi.append((rsi[i] - min_rsi) / (max_rsi - min_rsi))

    # Step 2: smooth for %K
    for i in range(len(stoch_rsi)):
        if stoch_rsi[i] is None or i < smooth_k - 1:
            k_values.append(None)
        else:
            window = [x for x in stoch_rsi[i - smooth_k + 1: i + 1] if x is not None]
            k_values.append(sum(window) / len(window))

    for i in range(len(k_values)):
        if k_values[i] is None or i < smooth_d - 1:
            d_values.append(None)
        else:
            window = [x for x in k_values[i - smooth_d + 1: i + 1] if x is not None]
            d_values.append(sum(window) / len(window))

    return k_values, d_values

def fetchData(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="100d", interval="1d")
    result = {
        "Date": [d.strftime("%Y-%m-%d") for d in hist.index.to_pydatetime()],
        "Open": hist["Open"].tolist(),
        "High": hist["High"].tolist(),
        "Low": hist["Low"].tolist(),
        "Close": hist["Close"].tolist(),
        "Volume": hist["Volume"].tolist()
    }
    return result

tickers = [
    # 1. NASDAQ-100 (~100 tickers)
    "ADBE","AMD","ABNB","GOOGL","GOOG","AMZN","AEP","AMGN","ADI","AAPL","AMAT","APP","ARM","ASML","AZN","TEAM","ADSK",
    "ADP","AXON","BKR","BIIB","BKNG","AVGO","CDNS","CDW","CHTR","CTAS","CSCO","CCEP","CTSH","CMCSA","CEG","CPRT","CSGP",
    "COST","CRWD","CSX","DDOG","DXCM","FANG","DASH","EA","EXC","FAST","FTNT","GEHC","GILD","GFS","HON","IDXX","INTC",
    "INTU","ISRG","KDP","KLAC","KHC","LRCX","LIN","LULU","MAR","MRVL","MELI","META","MCHP","MU","MSFT","MSTR","MDLZ",
    "MNST","NFLX","NVDA","NXPI","ORLY","ODFL","ON","PCAR","PLTR","PANW","PAYX","PYPL","PDD","PEP","QCOM","REGN","ROP",
    "ROST","SHOP","SBUX","SNPS","TMUS","TTWO","TSLA","TXN","TRI","TTD","VRSK","VRTX","WBD","WDAY","XEL","ZS",

    "GLD", "JPM","V","LLY","XOM","MA","JNJ","WMT","PG","BAC","UNH","HD","KO","PFE","CVX","VZ",
    "MRK","NKE","ABBV","DIS","MCD","SPGI","CRM","T","C","GE","USB","CAT","IBM","ORCL",
    "RTX","BBY","TMO","WFC","UPS","LOW","TJX","CL","SCHW","APD","BSX","BLK","PM","MS",
    "GS","ABT","DD","NOW","TM","MO","LRCX","BIIB","TSCO","PEP","MCO","LVS","EW","CME",
    "GM","F","KO","SYY","DE","EMR","MMM","CRM","ETN","GD","ICE","KEYS","LIN","NOC","SWKS",
    "RTX","CLX","PH","ITW","STZ","HWM","DHR","SPGI","D","MET","AFL","ALL","CINF","PGR",
    "TRV","AON","AJG","CB","WRB","MMC","J","ZTS","MOH","UHS","XRAY","EW","REG","LB",
    "ARE","PLD","PSA","CBRE","DLR","CCI","EQIX","SO","DUK","NEE","EXC","XEL","ETR","AEP","CMS","ES",
    "PEG","DTE","PCG","VLO","PSX","MPC","HES","COP","VTR","ESS","EQR","UDR","AVB","ARE","MAA","DLR"
]

for ticker in tickers:
    try:
        data = fetchData(ticker)
    except Exception as e:
        continue
    rsi=RSI(data)
    stochasticRSIK, stochasticRSID = StochRSI(data, rsi)
    bbPercent = BollingerBandsPercent(data)
    # Keys for the results json
    #
    # 2 = Overextended into buy side (ie rsi resting above 67.5)
    # 1 = Bullish action on the measure (ie rsi crossing from below 32.5 to above it)
    # 0 = Neither bear nor bull nor over extension (ie rsi sitting at 50)
    # -1 = bearish action on the indicator (ie rsi crossing from above 67.5 to below it)
    # -2 = Overextended into sell side (ie rsi resting below 32.5)
    results = {"rsi": 0, "bbPercent": 0, "stochasticRSIKCrossD": 0}

    if ((rsi[-3] > 67.5 and rsi[-1] < 67.5) or (rsi[-2] > 67.5 and rsi[-1] < 67.5)):
        results["rsi"] = -1
    elif ((rsi[-3] < 32.5 and rsi[-1] > 32.5) or (rsi[-2] < 32.5 and rsi[-1] > 32.5)):
        results["rsi"] = 1
    elif (rsi[-1] > 67.5):
        results["rsi"] = 2
    elif (rsi[-1] < 32.5):
        results["rsi"] = -2

    if ((stochasticRSIK[-3] > stochasticRSID[-3] and stochasticRSIK[-1] < stochasticRSID[-1]) or (stochasticRSIK[-2] > stochasticRSID[-2] and stochasticRSIK[-1] < stochasticRSID[-1])):
        results["stochasticRSIKCrossD"] = -1
    elif ((stochasticRSIK[-3] < stochasticRSID[-3] and stochasticRSIK[-1] > stochasticRSID[-1]) or (stochasticRSIK[-2] < stochasticRSID[-2] and stochasticRSIK[-1] > stochasticRSID[-1])):
        results["stochasticRSIKCrossD"] = 1

    if((bbPercent[-3] > .95 and bbPercent[-1] < .95) or (bbPercent[-2] > .95 and bbPercent[-1] < .95)):
        results["bbPercent"] = -1
    elif ((bbPercent[-3] < .05 and bbPercent[-1] > .05) or (bbPercent[-2] < .05 and bbPercent[-1] > .05)):
        results["bbPercent"] = 1
    elif (bbPercent[-1] > .95):
        results["bbPercent"] = 2
    elif (bbPercent[-1] < .05):
        results["bbPercent"] = -2

    percentBullish = 0
    percentBearish = 0
    percentNeutral = 0
    percentRestingHigh = 0
    percentRestingLow = 0
    for key, value in results.items():
        if value == 2:
            percentRestingHigh += 1
        elif value == 1:
            percentBullish += 1
        elif value == 0:
            percentNeutral += 1
        elif value == -1:
            percentBearish += 1
        elif value == -2:
            percentRestingLow += 1
    percentRestingHigh /= len(results)
    percentBullish /= len(results)
    percentNeutral /= len(results)
    percentBearish /= len(results)
    percentRestingLow /= len(results)

    print(f"{ticker} summary:\n", results, "\n", f"Percent resting high: {100*percentRestingHigh}\n", f"Percent bullish: {100*percentBullish}\n", f"Percent neutral: {100*percentNeutral}\n", f"Percent bearish: {100*percentBearish}\n", f"Percent resting low: {100*percentRestingLow}\n")
