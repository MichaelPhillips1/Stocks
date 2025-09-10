import statistics, yfinance as yf, requests
from datetime import datetime, timedelta, timezone

USER_EMAIL = "michaelphillips@vt.edu"
API_KEY = "0fckibnmSGatm+wER/gg1ZoVP8NReu+gdv7YMtWFzds="

def fetchDataProjectX(limit=40):
    BASE_URL = "https://api.topstepx.com"
    CONTRACT_ID = "CON.F.US.ENQ.U25"
    LIVE = True

    # 1) login -> bearer token
    auth = requests.post(
        f"{BASE_URL}/api/Auth/loginKey",
        headers={"accept": "text/plain", "Content-Type": "application/json"},
        json={"userName": USER_EMAIL, "apiKey": API_KEY},
        timeout=15
    )
    auth.raise_for_status()
    try:
        token = auth.json()["token"]
    except Exception:
        token = auth.text.strip().strip('"')
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2) get available contracts for your entitlement FIRST (more reliable than search)
    #    then fallback to search if needed.
    cid = None

    # 2a) available (live)
    try:
        avail = requests.post(
            f"{BASE_URL}/api/Contract/available",
            headers=headers,
            json={"live": LIVE},
            timeout=15
        )
        avail.raise_for_status()
        avail_list = avail.json() if isinstance(avail.json(), list) else avail.json().get("contracts", [])
        # pick ENQ first, then MNQ
        for c in avail_list:
            cid_str = str(c.get("id", ""))
            if ".ENQ." in cid_str:
                cid = cid_str
                break
        if not cid:
            for c in avail_list:
                cid_str = str(c.get("id", ""))
                if ".MNQ." in cid_str:
                    cid = cid_str;
                    break
    except Exception:
        pass

    # 2b) fallback: search "NQ"
    if not cid:
        s = requests.post(
            f"{BASE_URL}/api/Contract/search",
            headers=headers,
            json={"searchText": "NQ", "live": LIVE},
            timeout=15
        )
        s.raise_for_status()
        contracts = s.json().get("contracts", [])
        for c in contracts:
            cid_str = str(c.get("id", ""))
            if c.get("activeContract") and ".ENQ." in cid_str:
                cid = cid_str;
                break
        if not cid:
            for c in contracts:
                cid_str = str(c.get("id", ""))
                if c.get("activeContract") and ".MNQ." in cid_str:
                    cid = cid_str;
                    break
        # if still nothing, accept any ENQ/MNQ hit
        if not cid:
            for c in contracts:
                cid_str = str(c.get("id", ""))
                if ".ENQ." in cid_str or ".MNQ." in cid_str:
                    cid = cid_str;
                    break

    if not cid:
        raise RuntimeError("NQ not visible to your entitlement. Print Contract/available() to inspect what's returned.")

    # 3) time window for last N minutes
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=limit)

    payload = {
        "contractId": cid,
        "live": LIVE,
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "unit": 2,  # Minute
        "unitNumber": 1,  # 1-minute bars
        "limit": limit,
        "includePartialBar": True
    }

    bars = requests.post(
        f"{BASE_URL}/api/History/retrieveBars",
        headers=headers,
        json=payload,
        timeout=15
    )
    bars.raise_for_status()
    return bars.json()
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

def BuyOrSellSignal(bb, k, d, low=0.30, high=0.70):
    if not bb or not k or not d:
        return 0
    if len(bb) < 2 or len(k) < 2 or len(d) < 2:
        return 0

    b0 = bb[-1]
    k1, d1 = k[-1], d[-1]
    k0, d0 = k[-2], d[-2]

    if (b0 is None or k1 is None or d1 is None or k0 is None or d0 is None):
        return 0

    # SHORT: BB% > .90 and bearish cross (K from >= D to < D) while ABOVE deadzone
    if (b0 > 0.90 and
        k0 >= d0 and k1 < d1 and
        k0 > high and d0 > high and
        k1 > high and d1 > high):
        return -1

    # LONG: BB% < .10 and bullish cross (K from <= D to > D) while BELOW deadzone
    if (b0 < 0.10 and
        k0 <= d0 and k1 > d1 and
        k0 < low and d0 < low and
        k1 < low and d1 < low):
        return 1

    return 0