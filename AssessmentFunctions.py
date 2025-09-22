import statistics, yfinance as yf
import requests
from datetime import datetime, timedelta, timezone


def fetchDataProjectX(limit=40):
    BASE_URL    = "https://api.topstepx.com"
    USER_EMAIL = "michaelphillips@vt.edu"
    API_KEY = "MFHM2m9c9LN8aj9IKMVwEB/P3K49uwpmnfxRZXiPLro="
    CONTRACT_ID = "CON.F.US.ENQ.Z25"
    # 1) Authenticate -> JWT
    auth = requests.post(
        f"{BASE_URL}/api/Auth/loginKey",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"userName": USER_EMAIL, "apiKey": API_KEY},
        timeout=15
    )
    auth.raise_for_status()
    token = auth.json()["token"]
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=3)
    payload = {
        "contractId": CONTRACT_ID,
        "live": False,  # <- historical pull
        "startTime": start.isoformat().replace("+00:00", "Z"),
        "endTime": end.isoformat().replace("+00:00", "Z"),
        "unit": 1,  # 2 = Minute, 1 = Second
        "unitNumber": 5,  # X Minute or second bars
        "limit": int(limit),  # last N bars from the window
        "includePartialBar": True  # include the open/partial bar
    }
    r = requests.post(
        f"{BASE_URL}/api/History/retrieveBars",
        headers={
            "accept": "application/json",  # both work; prod often prefers JSON
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json=payload,
        timeout=30
    )
    data = r.json()
    bars = data.get("bars", [])
    bars.sort(key=lambda b: b.get("t", ""))
    return bars[-int(limit):]

def fetchDataYahoo(ticker, period="500d", interval="5d"):
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval=interval, auto_adjust=False, actions=False)
    hist = hist.dropna()
    result = {
        "Date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in hist.index.to_pydatetime()],
        "Open": hist["Open"].tolist(),
        "High": hist["High"].tolist(),
        "Low": hist["Low"].tolist(),
        "Close": hist["Close"].tolist(),
        "Volume": [int(v) if v == v else 0 for v in hist["Volume"].tolist()]
    }
    return result

def BollingerBandsPercent(data):
    closes = data["Close"]
    result = []
    for i in range(len(closes)):
        if i < 19:
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
    avg_gain = None
    avg_loss = None

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
            # Wilder smoothing
            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
            result.append(100 - (100 / (1 + rs)))

    return result

def StochasticRSI(data, rsi):
    period = 14
    smooth_k = 3
    smooth_d = 3

    stoch_rsi = []
    k_values = []
    d_values = []

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

    obv = [0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    return obv

def BuyOrSellSignal(stoch_k, stoch_d):
    """
    Pure Stochastic signal.
    Buy when %K crosses ABOVE %D (bullish cross)
    Sell when %K crosses BELOW %D (bearish cross)
    """
    n = min(len(stoch_k), len(stoch_d))
    if n < 2 or stoch_k[-1] is None or stoch_d[-1] is None:
        return 0

    k_prev, k_now = stoch_k[-2], stoch_k[-1]
    d_prev, d_now = stoch_d[-2], stoch_d[-1]

    # --- BUY: Bullish cross ---
    if k_prev is not None and d_prev is not None:
        if k_prev < d_prev and k_now > d_now:
            return 1

    # --- SELL: Bearish cross ---
    if k_prev is not None and d_prev is not None:
        if k_prev > d_prev and k_now < d_now:
            return -1

    return 0