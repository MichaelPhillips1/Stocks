import statistics, yfinance as yf

# ========================== ORIGINAL INDICATOR FUNCTIONS ======================

def BollingerBandsPercent(data):
    closes = data["Close"]
    result = []
    for i in range(len(closes)):
        if i < 19:
            result.append(None); continue
        window_slice = closes[i-19:i+1]
        sma = statistics.mean(window_slice)
        stdev = statistics.pstdev(window_slice)
        upper = sma + 2 * stdev
        lower = sma - 2 * stdev
        if upper == lower: result.append(None)
        else: result.append((closes[i] - lower) / (upper - lower))
    return result

def RSI(data):
    closes = data["Close"]
    result = []
    period = 14
    gains, losses = [], []
    for i in range(len(closes)):
        if i == 0:
            result.append(None); continue
        change = closes[i] - closes[i - 1]
        gain = max(change, 0); loss = -min(change, 0)
        gains.append(gain); losses.append(loss)
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
    period = 14; smooth_k = 3; smooth_d = 3
    stoch_rsi, k_values, d_values = [], [], []
    for i in range(len(rsi)):
        if rsi[i] is None or i < period:
            stoch_rsi.append(None); continue
        window = [x for x in rsi[i - period + 1: i + 1] if x is not None]
        if not window:
            stoch_rsi.append(None); continue
        min_rsi = min(window); max_rsi = max(window)
        if max_rsi == min_rsi: stoch_rsi.append(None)
        else: stoch_rsi.append((rsi[i] - min_rsi) / (max_rsi - min_rsi))
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
    closes = data["Close"]; volumes = data["Volume"]
    obv = [0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i-1]: obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i-1]: obv.append(obv[-1] - volumes[i])
        else: obv.append(obv[-1])
    return obv

def fetchData(ticker, period="500d", interval="5d"):
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval=interval, auto_adjust=False, actions=False).dropna()
    return {
        "Date":   [d.strftime("%Y-%m-%d %H:%M:%S") for d in hist.index.to_pydatetime()],
        "Open":   hist["Open"].tolist(),
        "High":   hist["High"].tolist(),
        "Low":    hist["Low"].tolist(),
        "Close":  hist["Close"].tolist(),
        "Volume": [int(v) if v == v else 0 for v in hist["Volume"].tolist()]
    }

def logResults(results):
    negative, positive, neutral = 0, 0, 0
    for _, value in results.items():
        if isinstance(value, str): continue
        if value < 0: negative += 1
        elif value > 0: positive += 1
        else: neutral += 1
    print(results); print("Negative:", negative, "Neutral:", neutral, "Positive:", positive)

def calcRSITopBottomCrossover(rsi):
    if ((rsi[-3] > 67.5 and rsi[-1] < 67.5) or (rsi[-2] > 67.5 and rsi[-1] < 67.5)): return -1
    elif ((rsi[-3] < 32.5 and rsi[-1] > 32.5) or (rsi[-2] < 32.5 and rsi[-1] > 32.5)): return 1
    return 0

def calcStochRSICrossover(stochasticRSIK, stochasticRSID):
    if (((stochasticRSIK[-3] > stochasticRSID[-3]) and (stochasticRSIK[-1] < stochasticRSID[-1])) or ((stochasticRSIK[-2] > stochasticRSID[-2]) and (stochasticRSIK[-1] < stochasticRSID[-1]))): return -1
    elif (((stochasticRSIK[-3] < stochasticRSID[-3]) and (stochasticRSIK[-1] > stochasticRSID[-1])) or ((stochasticRSIK[-2] < stochasticRSID[-2]) and (stochasticRSIK[-1] > stochasticRSID[-1]))): return 1
    return 0

def calcBollingerBandsPercentCrossover(bbPercent):
    if ((bbPercent[-3] > .9 and bbPercent[-1] < .9) or (bbPercent[-2] > .9 and bbPercent[-1] < .9)): return -1
    elif ((bbPercent[-3] < .1 and bbPercent[-1] > .1) or (bbPercent[-2] < .1 and bbPercent[-1] > .1)): return 1
    return 0

def calcOBVChange(obv):
    changeOne = obv[-1] - obv[-2]; changeTwo = obv[-1] - obv[-3]
    if ((changeOne < 0.02 * abs(obv[-2])) or (changeTwo < 0.02 * abs(obv[-2]))): return -1
    elif ((changeOne > 0.02 * abs(obv[-2])) or (changeTwo > 0.02 * abs(obv[-2]))): return 1
    else: return 0

def calcSignal(bb_score, rsi_score, stoch_score):
    if bb_score == -1 and rsi_score == -1 and stoch_score == -1: return -1
    if bb_score == 1 and rsi_score == 1 and stoch_score == 1: return 1
    return 0

# ============================== MINIMAL LOGIC =================================

def rsi_cross_down_67_5(rsi): return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] > 67.5 and rsi[-1] < 67.5
def rsi_cross_up_32_5(rsi):   return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] < 32.5 and rsi[-1] > 32.5

def stoch_cross_down(k, d):
    return (k[-2] is not None and d[-2] is not None and k[-1] is not None and d[-1] is not None and k[-2] >= d[-2] and k[-1] < d[-1])

def stoch_cross_up(k, d):
    return (k[-2] is not None and d[-2] is not None and k[-1] is not None and d[-1] is not None and k[-2] <= d[-2] and k[-1] > d[-1])

def bb_above_90(bb): return bb[-1] is not None and bb[-1] > 0.90
def bb_below_10(bb): return bb[-1] is not None and bb[-1] < 0.10

def stoch_deadzone_long(k, d, low=0.30):
    return (k[-2] is not None and d[-2] is not None and k[-1] is not None and d[-1] is not None and k[-2] < low and d[-2] < low and k[-1] < low and d[-1] < low)

def stoch_deadzone_short(k, d, high=0.70):
    return (k[-2] is not None and d[-2] is not None and k[-1] is not None and d[-1] is not None and k[-2] > high and d[-2] > high and k[-1] > high and d[-1] > high)

def entry_signal(bb, rsi, k, d):
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and stoch_deadzone_long(k, d, 0.30) and bb_below_10(bb): return 1
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and stoch_deadzone_short(k, d, 0.70) and bb_above_90(bb): return -1
    return 0

def opposite_signal_for_exit(bb, rsi, k, d):
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and bb_below_10(bb): return 1
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and bb_above_90(bb): return -1
    return 0

def practice_trade(
    data, bbPercent, rsi_list, stochK, stochD,
    fees_per_side=2.1, slip_pts=0.0, contract_multiplier=20.0,
    dollar_stop=100.0, take_profit_R=2.0
):
    closes = data["Close"]; dates = data["Date"]
    signals = []
    for i in range(len(closes)):
        if i < 3: signals.append(0); continue
        sig = entry_signal(bbPercent[:i+1], rsi_list[:i+1], stochK[:i+1], stochD[:i+1])
        signals.append(sig)
    pos = 0; entry_price = None; stop_px = None; target_px = None
    trades = []; realized = 0.0
    R_pts = (dollar_stop / contract_multiplier) if dollar_stop is not None else None
    for i in range(1, len(closes)):
        c = closes[i]; sig_now = signals[i]
        if pos != 0 and entry_price is not None:
            should_exit = False; exit_tag = None
            if R_pts is not None:
                if pos > 0 and c <= stop_px: should_exit = True; exit_tag = "stop"
                elif pos < 0 and c >= stop_px: should_exit = True; exit_tag = "stop"
            if not should_exit and take_profit_R is not None and R_pts is not None:
                if pos > 0 and c >= target_px: should_exit = True; exit_tag = "target"
                elif pos < 0 and c <= target_px: should_exit = True; exit_tag = "target"
            if not should_exit:
                opp = opposite_signal_for_exit(bbPercent[:i+1], rsi_list[:i+1], stochK[:i+1], stochD[:i+1])
                if (pos > 0 and opp == -1) or (pos < 0 and opp == 1): should_exit = True; exit_tag = "flip_exit"
            if should_exit:
                exit_px = c + (slip_pts if pos > 0 else -slip_pts)
                pnl_pts = (exit_px - entry_price) if pos > 0 else (entry_price - exit_px)
                pnl_dol = pnl_pts * contract_multiplier
                realized += pnl_dol - fees_per_side
                trades.append({"date": dates[i], "side": "SELL" if pos > 0 else "BUY", "qty": 1, "price": round(exit_px, 4), "pnl": round(pnl_dol - fees_per_side, 2), "tag": exit_tag})
                pos = 0; entry_price = None; stop_px = None; target_px = None
        if pos == 0:
            if sig_now == 1:
                fill_px = c - slip_pts; pos = 1; entry_price = fill_px
                if R_pts is not None:
                    stop_px = entry_price - R_pts
                    target_px = entry_price + (take_profit_R * R_pts if take_profit_R is not None else 0)
                trades.append({"date": dates[i], "side": "BUY", "qty": 1, "price": round(fill_px, 4), "pnl": 0.0, "tag": "entry"})
                realized -= fees_per_side
            elif sig_now == -1:
                fill_px = c + slip_pts; pos = -1; entry_price = fill_px
                if R_pts is not None:
                    stop_px = entry_price + R_pts
                    target_px = entry_price - (take_profit_R * R_pts if take_profit_R is not None else 0)
                trades.append({"date": dates[i], "side": "SELL", "qty": 1, "price": round(fill_px, 4), "pnl": 0.0, "tag": "entry"})
                realized -= fees_per_side
    if pos != 0 and entry_price is not None:
        c = closes[-1]
        exit_px = c + (slip_pts if pos > 0 else -slip_pts)
        pnl_pts = (exit_px - entry_price) if pos > 0 else (entry_price - exit_px)
        pnl_dol = pnl_pts * contract_multiplier
        realized += pnl_dol - fees_per_side
        trades.append({"date": dates[-1], "side": "SELL" if pos > 0 else "BUY", "qty": 1, "price": round(exit_px, 4), "pnl": round(pnl_dol - fees_per_side, 2), "tag": "final_exit"})
        pos = 0
    summary = {"trades": len(trades), "net_realized": round(realized, 2), "wins": sum(1 for t in trades if t["pnl"] > 0), "losses": sum(1 for t in trades if t["pnl"] < 0)}
    return summary, trades, signals, None

if __name__ == "__main__":
    import sys, requests

    # --- Fill these with YOUR creds (auth happens on TopstepX, not the gateway) ---
    AUTH_BASE = "https://api.topstepx.com"
    PROJECTX_EMAIL   = "michaelphillips@vt.edu".strip()
    PROJECTX_API_KEY = "0fckibnmSGatm+wER/gg1ZoVP8NReu+gdv7YMtWFzds=".strip()

    # --- 1) Ask once for your FIRM gateway URL (NOT the demo host) ---
    #     Example shape: https://gateway-api.<your-firm-domain>
    BASE = " https://api.topstepx.com".strip().rstrip("/")
    if not BASE.startswith("http"):
        print("No/invalid gateway URL provided. Exiting.")
        sys.exit(3)

    # --- Helpers (minimal) ---
    def explain_login_failure(js: dict):
        code = js.get("errorCode"); msg = js.get("errorMessage")
        print("\n[AUTH] loginKey failed.")
        print(f"       server payload: {js}")
        if code == 3:
            print("       Credentials not authorized (linking/entitlements).")
            print("       Fix:")
            print("         • TopstepX: Settings → API → ProjectX Linking")
            print("         • ProjectX: Subscriptions → API Access + CME NQ/MNQ entitlement")
            print("         • Email for loginKey must match dashboard email")
        if msg: print(f"       Server message: {msg}")

    def login_key(email: str, api_key: str) -> str:
        r = requests.post(f"{AUTH_BASE}/api/Auth/loginKey",
                          json={"userName": email, "apiKey": api_key},
                          headers={"accept": "text/plain", "Content-Type": "application/json"},
                          timeout=20)
        r.raise_for_status()
        js = r.json()
        if not js.get("success"):
            explain_login_failure(js); sys.exit(2)
        tok = js.get("token")
        if not tok:
            print("[AUTH] loginKey succeeded but no token returned."); print(js); sys.exit(2)
        return tok

    def validate(tok: str) -> str:
        r = requests.post(f"{AUTH_BASE}/api/Auth/validate",
                          headers={"Authorization": f"Bearer {tok}"},
                          timeout=20)
        r.raise_for_status()
        js = r.json()
        if js.get("success") and js.get("newToken"):
            return js["newToken"]
        return tok

    def gw_post(tok: str, path: str, payload: dict, timeout=20):
        h = {"Authorization": f"Bearer {tok}"}
        r = requests.post(f"{BASE}{path}", json=payload, headers=h, timeout=timeout)
        if r.status_code == 401:
            # token refresh
            tok = validate(tok)
            h = {"Authorization": f"Bearer {tok}"}
            r = requests.post(f"{BASE}{path}", json=payload, headers=h, timeout=timeout)
        r.raise_for_status()
        try:
            return tok, r.json()
        except ValueError:
            return tok, {}

    # --- 2) Auth (TopstepX) ---
    token = login_key(PROJECTX_EMAIL, PROJECTX_API_KEY)
    token = validate(token)

    # --- 3) Prove gateway + entitlements: blank delayed search SHOULD return contracts ---
    print(f"\nGateway probe: {BASE}")
    token, js = gw_post(token, "/api/Contract/search", {"searchText": "", "live": False}, timeout=20)
    arr = js.get("contracts", []) if isinstance(js, dict) else []

    if not arr:
        print("\n[DATA] 0 contracts returned.")
        print("       This means either:")
        print("       • Wrong gateway URL (not your firm’s), OR")
        print("       • Your account isn’t linked/entitled on THIS gateway yet.")
        print("         Fix: TopstepX Linking + ProjectX API Access + CME NQ/MNQ entitlement.")
        sys.exit(3)

    # --- 4) Show a couple results and suggest the correct symbol format (single-digit year) ---
    print(f"[DATA] Contracts returned: {len(arr)} (showing first 3)")
    for c in arr[:3]:
        print("   symbol:", c.get("symbol"), "id:", c.get("id"))

    print("\nTip: use single-digit year codes, e.g. September 2025 = NQU5 or MNQU5 (not NQU25).")
    print("Next step: use the returned 'id' (e.g., CON.F.US.ENQ.U25) with /api/History/retrieveBars.")
