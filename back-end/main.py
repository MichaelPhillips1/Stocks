import time, datetime, requests, matplotlib.pyplot as plt, sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from assessmentFunctions import *


plt.switch_backend('TkAgg')
plt.style.use('dark_background')

class MyWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.setWindowTitle("Stock Technicals")
        self.setStyleSheet("background-color: #2F3136;")
        self.setGeometry(0, 0, width, height)

        self.tickerSymbolEntryLabel = QLabel("PLEASE ENTER A TICKER", self)
        self.tickerSymbolEntryLabel.setStyleSheet('''font-size: 13pt; color: white;''')
        self.tickerSymbolEntryLabel.setAlignment(Qt.AlignCenter)
        self.tickerSymbolEntryLabel.setGeometry(int(.45 * width), int(.05 * height) - 55, int(.1 * width), 50)

        self.tickerSymbolEntry = QLineEdit(self)
        self.tickerSymbolEntry.setStyleSheet('''background-color: white;
                                             font-size: 13pt;
                                             border-radius: 10px;''')
        self.tickerSymbolEntry.setAlignment(Qt.AlignCenter)
        self.tickerSymbolEntry.setGeometry(int(.45 * width), int(.04 * height), int(.1 * width), 50)
        self.tickerSymbolEntry.setPlaceholderText("Please Enter a Ticker")

        self.tickerSymbolSearchButton = QPushButton("SEARCH", self)
        self.tickerSymbolSearchButton.setStyleSheet('''font-size: 13pt; color: white;
                                                    border-radius: 10px;
                                                    border: 1px solid white;''')
        self.tickerSymbolSearchButton.setGeometry(int(.45 * width), int(.05 * height) + 55, int(.1 * width), 50)
        self.tickerSymbolSearchButton.clicked.connect(self.help)

        self.figure = Figure()
        self.chartEmbededFigure = FigureCanvas(self.figure)
        self.chartEmbededFigure.setParent(self)  
        self.chartEmbededFigure.setGeometry(int(.05 * width), int(.05 * height) + 115, int(.9 * width), int(height * .75))
    
    def help(self):
        CurrentDate = datetime.date.today()
        PreviousDate = CurrentDate - datetime.timedelta(days=7 * 52)
        try:
            data = parseDataPolygon(requests.get(f"https://api.polygon.io/v2/aggs/ticker/{self.tickerSymbolEntry.text().strip().upper()}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results'])
        except:
            return
        
        closePriceData, openPriceData, highPriceData, lowPriceData, volumeData = data[1], data[2], data[3], data[4], data[5]
        
        periodRSI = 14
        periodFastMacd = 12
        periodSlowMacd = 26
        signalPeriodMacd = 9
        williamsPeriod = 14

        rsi = calculateRSI(closePriceData, periodRSI)
        macd = calculateMACD(closePriceData, periodFastMacd, periodSlowMacd, signalPeriodMacd)
        fib = calculateFibonacciRetracements(closePriceData)
        williams_r = calculateWilliamsR(highPriceData, lowPriceData, closePriceData, williamsPeriod)

        self.figure.clear()
        axs = self.figure.subplots(2, 2)

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

        self.chartEmbededFigure.draw()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow(app.primaryScreen().size().width(), app.primaryScreen().size().height())
    window.show()
    sys.exit(app.exec_())