import time, datetime, requests, matplotlib.pyplot as plt
from assessmentFunctions import *
plt.switch_backend('TkAgg')
plt.style.use('dark_background')

CurrentDate = datetime.date.today()
PreviousDate = CurrentDate - datetime.timedelta(days=7 * 50)
while True:
    try:
        ticker = str(input("Please enter a ticker: ")).upper()
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = ParseData(request)
        currentPriceData = data[1]
    except:
        time.sleep(15)
        continue

    periodRSI = 14
    periodFastMacd = 12
    periodSlowMacd = 26
    signalPeriodMacd = 9

    rsi = calculateRSI(currentPriceData, periodRSI)
    macd = calculateMACD(currentPriceData, periodFastMacd, periodSlowMacd, signalPeriodMacd)

    fig, axs = plt.subplots(3,1, figsize=(13,13))

    # Plot the price
    axs[0].plot([i for i in range(len(currentPriceData))], currentPriceData, label=f"Price: {currentPriceData[-1]}")
    axs[0].set_xlabel("Time Scale (Days)")
    axs[0].set_ylabel("Price")
    axs[0].legend(loc="upper left")

    # Plot the RSI
    axs[1].plot([i + periodRSI + 1 for i in range(len(rsi))], rsi, label=f"RSI: {rsi[-1]}")
    axs[1].axhline(70, color='red', linestyle='--')
    axs[1].axhline(30, color='green', linestyle='--')
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
    axs[1].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)
    axs[1].set_xlabel("Time Scale (Days)")
    axs[1].set_ylabel("RSI")
    axs[1].legend(loc="upper left")

    # Plot the MACD
    axs[2].plot([i for i in range(len(macd[0]))], macd[0], color="red", label=f"Signal: {macd[0][-1]}")
    axs[2].plot([i for i in range(len(macd[1]))], macd[1], color="green", label=f"MACD: {macd[1][-1]}")
    axs[2].set_xlabel("Time Scale (Days)")
    axs[2].set_ylabel("MACD")
    axs[2].legend(loc="upper left")

    # Save the graph and wait for next api interval
    plt.savefig(f"./Charts/{ticker}_{CurrentDate}.png")
    time.sleep(15)