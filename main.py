from AssessmentFunctions import (
    # Original calculators only
    BollingerBandsPercent, RSI, StochasticRSI, BuyOrSellSignal, fetchDataYahoo, fetchDataProjectX
)

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

    # Build per-bar signals using ONLY BuyOrSellSignal
    signals = []
    for i in range(len(closes)):
        if i < 3:
            signals.append(0)
            continue
        sig = BuyOrSellSignal(bbPercent[:i+1], stochK[:i+1], stochD[:i+1])
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

            # 3) Opposite signal check using ONLY BuyOrSellSignal
            if not should_exit:
                opp = BuyOrSellSignal(bbPercent[:i+1], stochK[:i+1], stochD[:i+1])
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

        # Entries (use BuyOrSellSignal only)
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

    summary = {
        "trades": len(trades),
        "net_realized": round(realized, 2),
        "wins": sum(1 for t in trades if t["pnl"] > 0),
        "losses": sum(1 for t in trades if t["pnl"] < 0),
    }
    return summary, trades, signals, None

if __name__ == "__main__":
    # ticker = "NQ=F"
    # period = "8d"
    # interval = "1m"
    # contract_multiplier = 20.0
    #
    # data = fetchDataYahoo(ticker, period=period, interval=interval)
    #
    # rsi_vals = RSI(data)
    # stochK, stochD = StochasticRSI(data, rsi_vals)
    # bbPercent = BollingerBandsPercent(data)
    #
    # # Use ONLY the single signal function here
    # last_signal = BuyOrSellSignal(bbPercent, stochK, stochD)
    # results = {
    #     "ticker": ticker,
    #     "BuyOrSellSignal": last_signal  # 1=Long, -1=Short, 0=None
    # }
    #
    # summary, trades, signals, _ = practice_trade(
    #     data, bbPercent, rsi_vals, stochK, stochD,
    #     fees_per_side=2.1,
    #     slip_pts=0.0,
    #     contract_multiplier=contract_multiplier,
    #     dollar_stop=250.0,
    #     take_profit_R=2.0,
    # )
    # print("\n=== PRACTICE SUMMARY ===")
    # print(summary)
    # for element in trades:
    #     if not element['pnl'] == 0.0:
    #         print(element)
    fetchDataProjectX(limit=40)