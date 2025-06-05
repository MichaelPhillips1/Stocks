import time, datetime, requests, matplotlib.pyplot as plt
from assessmentFunctions import *
plt.switch_backend('TkAgg')
plt.style.use('dark_background')

CurrentDate = datetime.date.today()
PreviousDate = CurrentDate - datetime.timedelta(days=7 * 52)
while True:
    try:
        ticker = str(input("Please enter a ticker: ")).upper()
        request = requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results']
        data = parseDataPolygon(request)
        closePriceData, openPriceData, highPriceData, lowPriceData, volumeData = data[1], data[2], data[3]. data[4], data[5]
        try:
            newPrice = float(input(f"Current daily price: {closePriceData[-1]}\n"
                                   f"Enter a current daily price or -1 to skip: "))
            if(newPrice != -1):
                closePriceData.append(newPrice)
        except:
            pass
    except:
        time.sleep(15)
        continue

    periodRSI = 14
    periodFastMacd = 12
    periodSlowMacd = 26
    signalPeriodMacd = 9
    williamsPeriod = 14

    rsi = calculateRSI(closePriceData, periodRSI)
    macd = calculateMACD(closePriceData, periodFastMacd, periodSlowMacd, signalPeriodMacd)
    fib = calculateFibonacciRetracements(closePriceData)
    williams_r = calculateWilliamsR(highPriceData, lowPriceData, closePriceData, williamsPeriod)

    fig, axs = plt.subplots(2, 2, figsize=(13,13), constrained_layout=True)

    # Plot the Fibonacci Retracements
    axs[0, 0].plot(range(len(closePriceData)), closePriceData, label="Price", linewidth=1.5)
    labels = ['0.0%', '23.6%', '38.2%', '50.0%', '61.8%', '78.6%', '100.0%']
    for lvl, label in zip(fib, labels):
        axs[0, 0].axhline(y=lvl, linestyle='--', linewidth=1, alpha=0.7)
        axs[0, 0].text(len(closePriceData) - 1, lvl, label, va='center', ha='right', fontsize=8)

    axs[0, 0].set_title("Fibonacci Retracement")
    axs[0, 0].set_xlabel("Time Scale (Days)")
    axs[0, 0].set_ylabel("Price")
    axs[0, 0].legend()

    # Plot the RSI
    axs[1, 0].plot([i + periodRSI + 1 for i in range(len(rsi))], rsi, label=f"RSI: {rsi[-1]}")
    axs[1, 0].axhline(70, color='red', linestyle='--')
    axs[1, 0].axhline(30, color='green', linestyle='--')
    axs[1, 0].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
    axs[1, 0].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)
    axs[1, 0].set_title("RSI")
    axs[1, 0].set_xlabel("Time Scale (Days)")
    axs[1, 0].set_ylabel("RSI")

    # Plot the MACD
    axs[0, 1].plot([i for i in range(len(macd[0]))], macd[0], color="red", label=f"Signal: {macd[0][-1]}")
    axs[0, 1].plot([i for i in range(len(macd[1]))], macd[1], color="green", label=f"MACD: {macd[1][-1]}")
    axs[0, 1].set_title("MACD")
    axs[0, 1].set_xlabel("Time Scale (Days)")
    axs[0, 1].set_ylabel("MACD")

    # Plot the Volume
    axs[1, 1].plot(range(len(volumeData)), volumeData, label="volume", linewidth=1.5)
    axs[1, 1].set_title("Volume")
    axs[1, 1].set_xlabel("Time Scale (Days)")
    axs[1, 1].set_ylabel("Volume")
    axs[1, 1].legend()

    # Save the graph and wait for next api interval
    plt.savefig(f"./Charts/{ticker}_{CurrentDate}.png")
    plt.show()