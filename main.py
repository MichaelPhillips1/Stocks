import time
from AssessmentFunctions import (
    BollingerBandsPercent, RSI, StochasticRSI, fetchDataProjectX
)

while True:
    time.sleep(1)
    fetchedData = fetchDataProjectX(limit=1000)
    o, h, l, c, v = [], [], [], [], []
    for element in fetchedData:
        o.append(element["o"])
        h.append(element["h"])
        l.append(element["l"])
        c.append(element["c"])
        v.append(element["v"])
    data = {"Open": o, "High": h, "Low": l, "Close": c, "Volume": v}
    rsi = RSI(data)
    stochK, stochD = StochasticRSI(data, rsi)
    bbPercent = BollingerBandsPercent(data)
