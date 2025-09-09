import statistics

# =============================================================================
# ======================= INDICATOR: BOLLINGER BANDS % =========================
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

def bb_above_90(bb):
    return bb[-1] is not None and bb[-1] > 0.90

def bb_below_10(bb):
    return bb[-1] is not None and bb[-1] < 0.10

def calcBollingerBandsPercentCrossover(bbPercent):
    if ((bbPercent[-3] > .9 and bbPercent[-1] < .9) or (bbPercent[-2] > .9 and bbPercent[-1] < .9)):
        return -1
    elif ((bbPercent[-3] < .1 and bbPercent[-1] > .1) or (bbPercent[-2] < .1 and bbPercent[-1] > .1)):
        return 1
    return 0


# =============================================================================
# =============================== INDICATOR: RSI ===============================
# =============================================================================

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

def rsi_cross_down_67_5(rsi):
    return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] > 67.5 and rsi[-1] < 67.5

def rsi_cross_up_32_5(rsi):
    return rsi[-2] is not None and rsi[-1] is not None and rsi[-2] < 32.5 and rsi[-1] > 32.5

def calcRSITopBottomCrossover(rsi):
    if ((rsi[-3] > 67.5 and rsi[-1] < 67.5) or (rsi[-2] > 67.5 and rsi[-1] < 67.5)):
        return -1
    elif ((rsi[-3] < 32.5 and rsi[-1] > 32.5) or (rsi[-2] < 32.5 and rsi[-1] > 32.5)):
        return 1
    return 0


# =============================================================================
# ============================ INDICATOR: STOCH RSI ============================
# =============================================================================

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

def calcStochRSICrossover(stochasticRSIK, stochasticRSID):
    if (((stochasticRSIK[-3] > stochasticRSID[-3]) and (stochasticRSIK[-1] < stochasticRSID[-1])) or ((stochasticRSIK[-2] > stochasticRSID[-2]) and (stochasticRSIK[-1] < stochasticRSID[-1]))):
        return -1
    elif (((stochasticRSIK[-3] < stochasticRSID[-3]) and (stochasticRSIK[-1] > stochasticRSID[-1])) or ((stochasticRSIK[-2] < stochasticRSID[-2]) and (stochasticRSIK[-1] > stochasticRSID[-1]))):
        return 1
    return 0


# =============================================================================
# ================================ INDICATOR: OBV ==============================
# =============================================================================

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

def calcOBVChange(obv):
    changeOne = obv[-1] - obv[-2]
    changeTwo = obv[-1] - obv[-3]
    if ((changeOne < 0.02 * abs(obv[-2])) or (changeTwo < 0.02 * abs(obv[-2]))):
        return -1
    elif ((changeOne > 0.02 * abs(obv[-2])) or (changeTwo > 0.02 * abs(obv[-2]))):
        return 1
    else:
        return 0


# =============================================================================
# ======================== COMPOSITE / STRATEGY ASSESSMENTS ====================
# =============================================================================

def entry_signal(bb, rsi, k, d):
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and stoch_deadzone_long(k, d, 0.30) and bb_below_10(bb):
        return 1
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and stoch_deadzone_short(k, d, 0.70) and bb_above_90(bb):
        return -1
    return 0

def opposite_signal_for_exit(bb, rsi, k, d):
    if rsi_cross_up_32_5(rsi) and stoch_cross_up(k, d) and bb_below_10(bb):
        return 1
    if rsi_cross_down_67_5(rsi) and stoch_cross_down(k, d) and bb_above_90(bb):
        return -1
    return 0

def calcSignal(bb_score, rsi_score, stoch_score):
    if bb_score == -1 and rsi_score == -1 and stoch_score == -1:
        return -1
    if bb_score == 1 and rsi_score == 1 and stoch_score == 1:
        return 1
    return 0
