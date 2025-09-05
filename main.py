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


def StochasticRSI(data, rsi):
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

def OBV(data):
    closes = data["Close"]
    volumes = data["Volume"]

    obv = [0]  # start at zero
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])  # no change

    return obv

def fetchData(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="500d", interval="5d")
    result = {
        "Date": [d.strftime("%Y-%m-%d") for d in hist.index.to_pydatetime()],
        "Open": hist["Open"].tolist(),
        "High": hist["High"].tolist(),
        "Low": hist["Low"].tolist(),
        "Close": hist["Close"].tolist(),
        "Volume": hist["Volume"].tolist()
    }
    return result

def calcRSITopBottomCrossover(rsi):
    if ((rsi[-3] > 67.5 and rsi[-1] < 67.5) or (rsi[-2] > 67.5 and rsi[-1] < 67.5)):
        return -1
    elif ((rsi[-3] < 32.5 and rsi[-1] > 32.5) or (rsi[-2] < 32.5 and rsi[-1] > 32.5)):
        return 1
    return 0

def calcStochRSICrossover(stochasticRSIK, stochasticRSID):
    if (((stochasticRSIK[-3] > stochasticRSID[-3]) and (stochasticRSIK[-1] < stochasticRSID[-1])) or ((stochasticRSIK[-2] > stochasticRSID[-2]) and (stochasticRSIK[-1] < stochasticRSID[-1]))):
        return -1
    elif (((stochasticRSIK[-3] < stochasticRSID[-3]) and (stochasticRSIK[-1] > stochasticRSID[-1])) or ((stochasticRSIK[-2] < stochasticRSID[-2]) and (stochasticRSIK[-1] > stochasticRSID[-1]))):
        return 1
    return 0

def calcBollingerBandsPercentCrossover(bbPercent):
    if ((bbPercent[-3] > .95 and bbPercent[-1] < .95) or (bbPercent[-2] > .95 and bbPercent[-1] < .95)):
        return -1
    elif ((bbPercent[-3] < .05 and bbPercent[-1] > .05) or (bbPercent[-2] < .05 and bbPercent[-1] > .05)):
        return 1
    return 0

def calcOBVChange(obv):
    changeOne = obv[-1] - obv[-2]
    changeTwo = obv[-1] - obv[-3]
    if ((changeOne < 0.02 * abs(obv[-2])) or (changeTwo < 0.02 * abs(obv[-2]))):
        return -1
    elif ((changeOne > 0.02 * abs(obv[-2])) or (changeTwo > 0.02 * abs(obv[-2]))):  # >2% jump
        return 1
    else:
        return 0

tickers =  [
    # --- Tech & Semiconductors ---
    "NVDA","AMD","TSLA","SMCI","MU","ON","WOLF","MRVL","INTC","QCOM",
    "AVGO","ASML","LRCX","AMAT","KLAC","NXPI","ADI","SWKS","TER","COHR",
    "ACLS","ALGM","AEHR","UCTT","UCTT","COHR","ONTO","FORM","KLIC","SGH",
    "LSCC","CDNS","SNPS","ANSS","ADBE","INTU","CRM","ORCL","MSFT","AAPL",
    "META","GOOG","GOOGL","PANW","ZS","CRWD","DDOG","SNOW","MDB","OKTA",
    "NET","BILL","APP","DOCN","TEAM","NOW","MNDY","ASAN","HUBS","PATH",
    "DT","ESTC","SPLK","NTNX","CFLT","TWLO","ZM","SHOP","AFRM","UPST",

    # --- E-Commerce / Consumer Discretionary ---
    "ABNB","UBER","LYFT","BKNG","ETSY","ROKU","PTON","RIVN","LCID","XPEV",
    "LI","NIO","BYDDF","MELI","CPNG","JD","BABA","PDD","SE","W","TSCO",
    "AMZN","TGT","COST","WMT","BBY","HD","LOW","CVNA","KMX","DKNG","PENN",
    "MGM","LVS","WYNN","EXPE","TRIP","SBUX","CMG","MCD","YUM","DPZ",
    "ANF","URBN","AEO","CROX","ONON","NKE","LULU","DECK","UAA","SKX",

    # --- Financials & Fintech ---
    "SQ","PYPL","COIN","HOOD","SOFI","ALLY","AXP","DFS","C","BAC",
    "JPM","MS","GS","SCHW","CME","ICE","BLK","KKR","BX","CG",
    "AMP","MTB","FITB","KEY","HBAN","RF","PNC","TFC","ZION","CFR",

    # --- Energy / Materials ---
    "OXY","DVN","FANG","MRO","APA","HES","PXD","CLR","EOG","CVX",
    "XOM","COP","SU","CNQ","ENB","TRP","KMI","WMB","OKE","LNG",
    "FCX","AA","NUE","STLD","CLF","X","VALE","TECK","RIO","SCCO",
    "CMC","ATI","MT","MOS","CF","NTR","IPI","LXU","ALB","LTHM",
    "PLL","SGML","LAC","FMC","DD","CE","DOW","EMN","HUN","OLN",

    # --- Industrials / Airlines / EVs ---
    "CAT","DE","GE","HON","MMM","BA","LMT","RTX","NOC","GD",
    "DAL","UAL","AAL","LUV","ALK","JBLU","SAVE","HA","CCL","RCL",
    "NCLH","F","GM","STLA","TM","HMC","VWAGY","TT","EMR","ETN",
    "ROK","PH","ITW","GWW","FAST","URI","CMI","PCAR","SWK","MAS",
    "DHI","LEN","TOL","PHM","KBH","MTH","BLDR","OC","EXP","USG",

    # --- Healthcare / Biopharma (liquid, not tiny biotech) ---
    "VRTX","REGN","BIIB","GILD","MRNA","BNTX","ALNY","INCY","EXAS","ILMN",
    "DXCM","IDXX","TDOC","PEN","ISRG","EW","ABMD","SYK","ZBH","BSX",
    "UNH","HUM","CI","ELV","CNC","MOH","DGX","LH","IQV","RGEN",
    "TECH","BRKR","TMO","DHR","A","WAT","MTD","BIO","QDEL","HOLX",

    # --- Media / Communication Services ---
    "NFLX","DIS","CMCSA","PARA","WBD","SPOT","TTWO","EA","ROKU","CHTR",
    "TMUS","VZ","T","DISH","NWSA","NWS","BIDU","IQ","SIRI","WB",

    # --- Utilities / REITs (select high beta relative to sector) ---
    "NEE","DUK","D","SO","EXC","PEG","ED","AEP","PPL","EIX",
    "SPG","O","DLR","EQIX","PLD","AMT","CCI","SBAC","VICI","WY"
]

for ticker in tickers:
    try:
        data = fetchData(ticker)
        rsi = RSI(data)
        stochasticRSIK, stochasticRSID = StochasticRSI(data, rsi)
        bbPercent = BollingerBandsPercent(data)
        obv = OBV(data)
        results = {"ticker": ticker, "rsiTopBottomCrossover": calcRSITopBottomCrossover(rsi),
                   "bbPercentCrossover": calcBollingerBandsPercentCrossover(bbPercent),
                   "stochasticRSICrossover": calcStochRSICrossover(stochasticRSIK, stochasticRSID), "obvChange": calcOBVChange(obv)}
        totalScore = (results["rsiTopBottomCrossover"] + results["bbPercentCrossover"] + results["stochasticRSICrossover"] + results["obvChange"])
        print(results, str(totalScore) + "/4")
    except Exception as e:
        continue