import statistics, yfinance as yf

# =============================================================================
# ========================== ORIGINAL INDICATOR FUNCTIONS ======================
# =============================================================================

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

def fetchData(ticker, period="500d", interval="5d"):
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

def logResults(results):
    negative, positive, neutral = 0, 0, 0
    for key, value in results.items():
        if (type(value) == str):
            continue
        if (value < 0):
            negative += 1
        elif (value > 0):
            positive += 1
        else:
            neutral += 1
    print(results)
    print("Negative:", negative, "Neutral:", neutral, "Positive:", positive)

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
    if ((bbPercent[-3] > .9 and bbPercent[-1] < .9) or (bbPercent[-2] > .9 and bbPercent[-1] < .9)):
        return -1
    elif ((bbPercent[-3] < .1 and bbPercent[-1] > .1) or (bbPercent[-2] < .1 and bbPercent[-1] > .1)):
        return 1
    return 0

def calcOBVChange(obv):
    changeOne = obv[-1] - obv[-2]
    changeTwo = obv[-1] - obv[-3]
    if ((changeOne < 0.02 * abs(obv[-2])) or (changeTwo < 0.02 * abs(obv[-2]))):
        return -1
    elif ((changeOne > 0.02 * abs(obv[-2])) or (changeTwo > 0.02 * abs(obv[-2]))):
        return 1
    else:
        return 0

def calcSignal(bb_score, rsi_score, stoch_score):
    if bb_score == -1 and rsi_score == -1 and stoch_score == -1:
        return -1
    if bb_score == 1 and rsi_score == 1 and stoch_score == 1:
        return 1
    return 0

# =============================================================================
# ============================== MINIMAL LOGIC =================================
# =============================================================================

def rsi_cross_down_67_5(rsi):
    return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] > 67.5 and rsi[-1] < 67.5

def rsi_cross_up_32_5(rsi):
    return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] < 32.5 and rsi[-1] > 32.5

def stoch_cross_down(k, d):
    return (
        k[-2] is not None and d[-2] is not None and
        k[-1] is not None and d[-1] is not None and
        k[-2] >= d[-2] and k[-1] < d[-1]
    )

def stoch_cross_up(k, d):
    return (
        k[-2] is not None and d[-2] is not None and
        k[-1] is not None and d[-1] is not None and
        k[-2] <= d[-2] and k[-1] > d[-1]
    )

def bb_above_90(bb):
    return bb[-1] is not None and bb[-1] > 0.90

def bb_below_10(bb):
    return bb[-1] is not None and bb[-1] < 0.10

def stoch_deadzone_long(k, d, low=0.30):
    return (
        k[-2] is not None and d[-2] is not None and
        k[-1] is not None and d[-1] is not None and
        k[-2] < low and d[-2] < low and
        k[-1] < low and d[-1] < low
    )

def stoch_deadzone_short(k, d, high=0.70):
    return (
        k[-2] is not None and d[-2] is not None and
        k[-1] is not None and d[-1] is not None and
        k[-2] > high and d[-2] > high and
        k[-1] > high and d[-1] > high
    )

def entry_signal(bb, rsi, k, d):
    # LONG: RSI up cross, Stoch K>D cross in <0.30 dead-zone, BB% < 0.10
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and stoch_deadzone_long(k, d, 0.30) and bb_below_10(bb):
        return 1
    # SHORT: RSI down cross, Stoch K<D cross in >0.70 dead-zone, BB% > 0.90
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and stoch_deadzone_short(k, d, 0.70) and bb_above_90(bb):
        return -1
    return 0

def opposite_signal_for_exit(bb, rsi, k, d):
    # No dead-zone gating for exits; only the 0.10/0.90 BB% + RSI cross + Stoch cross
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and bb_below_10(bb):
        return 1
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and bb_above_90(bb):
        return -1
    return 0

def practice_trade(
    data,
    bbPercent,
    rsi_list,
    stochK,
    stochD,
    fees_per_side=2.1,
    slip_pts=0.0,
    contract_multiplier=20.0,
    dollar_stop=100.0,
    take_profit_R=2.0
):
    closes = data["Close"]
    dates  = data["Date"]

    signals = []
    for i in range(len(closes)):
        if i < 3:
            signals.append(0)
            continue
        sig = entry_signal(bbPercent[:i+1], rsi_list[:i+1], stochK[:i+1], stochD[:i+1])
        signals.append(sig)

    pos = 0
    entry_price = None
    stop_px = None
    target_px = None
    trades = []
    realized = 0.0
    R_pts = (dollar_stop / contract_multiplier) if dollar_stop is not None else None

    for i in range(1, len(closes)):
        c = closes[i]
        sig_now = signals[i]

        if pos != 0 and entry_price is not None:
            should_exit = False
            exit_tag = None

            # 1) Stop check
            if R_pts is not None:
                if pos > 0 and c <= stop_px:
                    should_exit = True; exit_tag = "stop"
                elif pos < 0 and c >= stop_px:
                    should_exit = True; exit_tag = "stop"

            # 2) Target check
            if not should_exit and take_profit_R is not None and R_pts is not None:
                if pos > 0 and c >= target_px:
                    should_exit = True; exit_tag = "target"
                elif pos < 0 and c <= target_px:
                    should_exit = True; exit_tag = "target"

            # 3) Opposite signal (flip) check
            if not should_exit:
                opp = opposite_signal_for_exit(bbPercent[:i+1], rsi_list[:i+1], stochK[:i+1], stochD[:i+1])
                if (pos > 0 and opp == -1) or (pos < 0 and opp == 1):
                    should_exit = True; exit_tag = "flip_exit"

            if should_exit:
                exit_px = c + (slip_pts if pos > 0 else -slip_pts)
                pnl_pts = (exit_px - entry_price) if pos > 0 else (entry_price - exit_px)
                pnl_dol = pnl_pts * contract_multiplier
                realized += pnl_dol - fees_per_side
                trades.append({
                    "date": dates[i],
                    "side": "SELL" if pos > 0 else "BUY",
                    "qty": 1,
                    "price": round(exit_px, 4),
                    "pnl": round(pnl_dol - fees_per_side, 2),
                    "tag": exit_tag
                })
                pos = 0
                entry_price = None
                stop_px = None
                target_px = None

        # Entries
        if pos == 0:
            if sig_now == 1:
                fill_px = c - slip_pts
                pos = 1
                entry_price = fill_px
                if R_pts is not None:
                    stop_px = entry_price - R_pts
                    target_px = entry_price + (take_profit_R * R_pts if take_profit_R is not None else 0)
                trades.append({"date": dates[i], "side": "BUY", "qty": 1, "price": round(fill_px, 4), "pnl": 0.0, "tag": "entry"})
                realized -= fees_per_side
            elif sig_now == -1:
                fill_px = c + slip_pts
                pos = -1
                entry_price = fill_px
                if R_pts is not None:
                    stop_px = entry_price + R_pts
                    target_px = entry_price - (take_profit_R * R_pts if take_profit_R is not None else 0)
                trades.append({"date": dates[i], "side": "SELL", "qty": 1, "price": round(fill_px, 4), "pnl": 0.0, "tag": "entry"})
                realized -= fees_per_side

    # Final exit on last bar
    if pos != 0 and entry_price is not None:
        c = closes[-1]
        exit_px = c + (slip_pts if pos > 0 else -slip_pts)
        pnl_pts = (exit_px - entry_price) if pos > 0 else (entry_price - exit_px)
        pnl_dol = pnl_pts * contract_multiplier
        realized += pnl_dol - fees_per_side
        trades.append({
            "date": dates[-1],
            "side": "SELL" if pos > 0 else "BUY",
            "qty": 1,
            "price": round(exit_px, 4),
            "pnl": round(pnl_dol - fees_per_side, 2),
            "tag": "final_exit"
        })
        pos = 0

    summary = {
        "trades": len(trades),
        "net_realized": round(realized, 2),
        "wins": sum(1 for t in trades if t["pnl"] > 0),
        "losses": sum(1 for t in trades if t["pnl"] < 0),
    }
    return summary, trades, signals, None

if __name__ == "__main__":
    import sys, time, requests, pandas as pd
    from datetime import datetime, timedelta, timezone

    # ===== Your creds (unchanged) ============================================
    PROJECTX_EMAIL   = "michaelphillips@vt.edu".strip()
    PROJECTX_API_KEY = "0fckibnmSGatm+wER/gg1ZoVP8NReu+gdv7YMtWFzds=".strip()
    BASE = "https://gateway-api-demo.s2f.projectx.com"  # use demo host only
    # ========================================================================

    # Runtime config
    symbol_search_text = "NQ"    # or "MNQ"
    contract_multiplier = 20.0
    lookback_minutes = 600
    poll_seconds = 2
    fees_per_side = 2.1
    slip_pts = 0.0
    dollar_stop = 100.0
    take_profit_R = 2.0
    LIVE_FEED = True
    ONLY_CLOSED_BARS = True

    sess = requests.Session()
    sess.headers.update({"Connection": "keep-alive"})
    sess.trust_env = True
    sess_timeout = 20

    # ---- helpers ------------------------------------------------------------
    def build_data_from_df(df: pd.DataFrame):
        idx = df.index
        if getattr(idx, "tz", None) is not None:
            idx = idx.tz_convert("UTC").tz_localize(None)
        return {
            "Date":   [d.strftime("%Y-%m-%d %H:%M:%S") for d in idx.to_pydatetime()],
            "Open":   df["Open"].astype(float).tolist(),
            "High":   df["High"].astype(float).tolist(),
            "Low":    df["Low"].astype(float).tolist(),
            "Close":  df["Close"].astype(float).tolist(),
            "Volume": [int(v) if v == v else 0 for v in df["Volume"].tolist()],
        }

    def explain_login_failure(js: dict):
        code = js.get("errorCode")
        msg  = js.get("errorMessage")
        print("\n[AUTH] loginKey failed.")
        print(f"       server payload: {js}")
        if code == 3:
            # Most common: wrong email for that API key OR API Access not enabled/linked
            print("       Meaning: credentials not accepted (email+API key not authorized).")
            print("       Fixes:")
            print("         1) In TopstepX: Settings → API → ProjectX Linking (link your account).")
            print("         2) In ProjectX dashboard: Subscriptions → enable API Access, then generate a fresh API key.")
            print("         3) Use the SAME email shown on the ProjectX dashboard for loginKey.")
            print("         4) Copy/paste the key exactly; no hidden spaces/newlines.")
            print("       (This is the common cause others reported for errorCode 3.)")
        else:
            print("       Check that API Access is active, account is linked, and the key/email pair is correct.")
        if msg:
            print(f"       Server message: {msg}")

    def px_login_key(base: str, email: str, api_key: str):
        r = sess.post(f"{base}/api/Auth/loginKey",
                      json={"userName": email, "apiKey": api_key},
                      timeout=sess_timeout)
        r.raise_for_status()
        js = r.json()
        if not js.get("success"):
            explain_login_failure(js)
            sys.exit(2)
        tok = js.get("token")
        if not tok:
            print("[AUTH] loginKey succeeded but no token field present.")
            print(f"       payload: {js}")
            sys.exit(2)
        return tok

    def px_validate(base: str, token: str) -> str:
        r = sess.post(f"{base}/api/Auth/validate",
                      headers={"Authorization": f"Bearer {token}"},
                      timeout=sess_timeout)
        r.raise_for_status()
        js = r.json()
        if js.get("success") and js.get("newToken"):
            return js["newToken"]
        return token

    def px_post(base: str, token: str, path: str, payload: dict, timeout=sess_timeout):
        h = {"Authorization": f"Bearer {token}"}
        r = sess.post(f"{base}{path}", json=payload, headers=h, timeout=timeout)
        if r.status_code == 401:
            token = px_validate(base, token)
            h = {"Authorization": f"Bearer {token}"}
            r = sess.post(f"{base}{path}", json=payload, headers=h, timeout=timeout)
        r.raise_for_status()
        try:
            return token, r.json()
        except ValueError:
            return token, {}

    def px_search_contract(base: str, token: str, q: str):
        token, js = px_post(base, token, "/api/Contract/search",
                            {"searchText": q, "live": LIVE_FEED}, timeout=15)
        arr = js.get("contracts", []) if isinstance(js, dict) else []
        if not arr:
            print("[DATA] No contracts returned. Verify API access & linking in your TopstepX/ProjectX dashboards.")
            sys.exit(3)
        arr.sort(key=lambda c: (("MNQ" in c.get("symbol","")), c.get("symbol","")))
        return token, arr[0]

    def px_get_last_minutes_bars(base: str, token: str, contract_id: str, minutes: int):
        end_utc = datetime.now(timezone.utc)
        start_utc = end_utc - timedelta(minutes=minutes)
        payload = {
            "contractId": contract_id,
            "live": LIVE_FEED,
            "startTime": start_utc.isoformat(),
            "endTime": end_utc.isoformat(),
            "unit": 2,                    # 2 = minute bars
            "unitNumber": 1,
            "limit": 20000,
            "includePartialBar": (not ONLY_CLOSED_BARS)
        }
        token, js = px_post(BASE, token, "/api/History/retrieveBars", payload, timeout=30)
        bars = js.get("bars", []) if isinstance(js, dict) else []
        if not bars:
            return token, pd.DataFrame()
        df = pd.DataFrame(bars).rename(columns={"t":"Datetime","o":"Open","h":"High","l":"Low","c":"Close","v":"Volume"})
        df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
        df = df.set_index("Datetime").sort_index()
        return token, df[["Open","High","Low","Close","Volume"]]

    # ---- boot (auth first; fail fast with guidance if not authorized) -------
    TOKEN = px_login_key(BASE, PROJECTX_EMAIL, PROJECTX_API_KEY)
    TOKEN = px_validate(BASE, TOKEN)

    TOKEN, contract = px_search_contract(BASE, TOKEN, symbol_search_text)
    contract_id = str(contract.get("id"))
    contract_sym = contract.get("symbol", "?")
    print(f"=== ProjectX LIVE (demo endpoint) === base={BASE}  contract={contract_sym} id={contract_id}")

    seen_trades = 0
    last_printed_bar = None
    pos_snapshot = 0

    while True:
        try:
            TOKEN, df = px_get_last_minutes_bars(BASE, TOKEN, contract_id, lookback_minutes)
            if df.empty:
                time.sleep(poll_seconds)
                continue

            data = build_data_from_df(df)

            # --- your indicators/logic (unchanged) ---
            rsi_vals = RSI(data)
            stochK, stochD = StochasticRSI(data, rsi_vals)
            bbPercent = BollingerBandsPercent(data)

            summary, trades, signals, _ = practice_trade(
                data, bbPercent, rsi_vals, stochK, stochD,
                fees_per_side=fees_per_side,
                slip_pts=slip_pts,
                contract_multiplier=contract_multiplier,
                dollar_stop=dollar_stop,
                take_profit_R=take_profit_R,
            )

            last_bar_str = data["Date"][-1]
            last_bar_utc = pd.to_datetime(last_bar_str, utc=True).to_pydatetime()
            latency = (datetime.now(timezone.utc) - last_bar_utc).total_seconds()

            if last_bar_str != last_printed_bar:
                last_printed_bar = last_bar_str
                last_close = data["Close"][-1]
                sig = signals[-1]
                sig_txt = "LONG" if sig == 1 else ("SHORT" if sig == -1 else "—")
                print(f"[{last_bar_str}Z] close={last_close:.2f}  signal={sig_txt}  latency={latency:.1f}s  pos={pos_snapshot}")

            if len(trades) > seen_trades:
                for t in trades[seen_trades:]:
                    print(f"TRADE: {t['date']}  {t['side']} @ {t['price']}  pnl={t['pnl']}  tag={t['tag']}")
                    if t["tag"] == "entry":
                        pos_snapshot = 1 if t["side"] == "BUY" else -1
                    elif t["tag"] in ("stop","target","flip_exit","final_exit"):
                        pos_snapshot = 0
                seen_trades = len(trades)

        except requests.RequestException as e:
            print(f"[net] {type(e).__name__}: {e}. Retrying in {poll_seconds}s...")
        except Exception as e:
            print(f"[err] {type(e).__name__}: {e}. Retrying in {poll_seconds}s...")
        time.sleep(poll_seconds)
