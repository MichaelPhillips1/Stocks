import time
from AssessmentFunctions import BollingerBandsPercent, RSI, StochasticRSI, BuyOrSellSignal, fetchDataProjectX

p=0
side=0
while True:
    time.sleep(1)
    fetchedData = fetchDataProjectX(limit=1000)
    o, h, l, c, v, t = [], [], [], [], [], []
    for element in fetchedData:
        o.append(element["o"])
        h.append(element["h"])
        l.append(element["l"])
        c.append(element["c"])
        v.append(element["v"])
        t.append(element["t"])
    data = {"Open": o, "High": h, "Low": l, "Close": c, "Volume": v, "Time": t}
    rsi = RSI(data)
    stochK, stochD = StochasticRSI(data, rsi)
    bbPercent = BollingerBandsPercent(data)
    signal = BuyOrSellSignal(stochK, stochD)
    if signal != 0:
        print(signal, data["Time"][-1])
        if side == 0:
            side = signal
            p = data["Close"][-1]
        elif signal != side:
            if side == 1:  # was long
                print("PnL:", data["Close"][-1] - p)
            elif side == -1:  # was short
                print("PnL:", p - data["Close"][-1])
            side = signal
            p = data["Close"][-1]