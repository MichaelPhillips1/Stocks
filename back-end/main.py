import time, datetime, requests, matplotlib.pyplot as plt, sys, json, threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QLabel, QPushButton, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from functools import partial
from assessmentFunctions import *
from openai import OpenAI

plt.switch_backend('TkAgg')
plt.style.use('dark_background')

class MyWindow(QMainWindow):
    def __init__(self, width, height):
        super().__init__()
        self.client = OpenAI(api_key="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")
        self.setWindowTitle("Stock Technicals")
        self.setStyleSheet("background-color: #2F3136;")
        self.setGeometry(0, 0, width, height)

        self.tickerSymbolEntryLabel = QLabel("PLEASE ENTER A TICKER, A DAY TIME PERIOD, AND A CURRENT PRICE IF APPLICABLE", self)
        self.tickerSymbolEntryLabel.setStyleSheet('''font-size: 13pt; color: white;''')
        self.tickerSymbolEntryLabel.setAlignment(Qt.AlignCenter)
        self.tickerSymbolEntryLabel.setGeometry(int(.3 * width), int(.05 * height) - 55, int(.4 * width), 50)

        self.tickerSymbolEntry = QLineEdit(self)
        self.tickerSymbolEntry.setStyleSheet('''background-color: white;
                                             font-size: 13pt;
                                             border-radius: 10px;''')
        self.tickerSymbolEntry.setAlignment(Qt.AlignCenter)
        self.tickerSymbolEntry.setGeometry(int(.345 * width), int(.04 * height), int(.1 * width), 50)
        self.tickerSymbolEntry.setPlaceholderText("Ticker")

        self.timePeriodDaysEntry = QLineEdit(self)
        self.timePeriodDaysEntry.setStyleSheet('''background-color: white;
                                             font-size: 13pt;
                                             border-radius: 10px;''')
        self.timePeriodDaysEntry.setAlignment(Qt.AlignCenter)
        self.timePeriodDaysEntry.setGeometry(int(.45 * width), int(.04 * height), int(.1 * width), 50)
        self.timePeriodDaysEntry.setPlaceholderText("Time Period (Days)")
        
        self.currentPriceEntry = QLineEdit(self)
        self.currentPriceEntry.setStyleSheet('''background-color: white;
                                             font-size: 13pt;
                                             border-radius: 10px;''')
        self.currentPriceEntry.setAlignment(Qt.AlignCenter)
        self.currentPriceEntry.setGeometry(int(.555 * width), int(.04 * height), int(.1 * width), 50)
        self.currentPriceEntry.setPlaceholderText("Current Price")

        self.tickerSymbolSearchButton = QPushButton("SEARCH", self)
        self.tickerSymbolSearchButton.setStyleSheet('''font-size: 13pt; color: white;
                                                    border-radius: 10px;
                                                    border: 1px solid white;''')
        self.tickerSymbolSearchButton.setGeometry(int(.45 * width), int(.05 * height) + 55, int(.1 * width), 50)
        self.tickerSymbolSearchButton.clicked.connect(self.initiateSearch)

        self.graphLeftButton = QPushButton("<", self)
        self.graphLeftButton.setStyleSheet('''font-size: 13pt; color: white;
                                                    border-radius: 10px;
                                                    border: 1px solid white;''')
        self.graphLeftButton.setGeometry(int(.02 * width), int(.475 * height), int(.02 * width), (int(.05 * height)))
        self.graphLeftButton.clicked.connect(self.initiateSearch)
        self.graphLeftButton.clicked.connect(partial(self.cycleGraphs, 0))


        self.graphRightButton = QPushButton(">", self)
        self.graphRightButton.setStyleSheet('''font-size: 13pt; color: white;
                                                    border-radius: 10px;
                                                    border: 1px solid white;''')
        self.graphRightButton.setGeometry(int(.96 * width), int(.475 * height), int(.02 * width), (int(.05 * height)))
        self.graphRightButton.clicked.connect(partial(self.cycleGraphs, 1))

        self.chartSlide = 0
        self.chartCollection = []

        self.figureTwo = Figure()
        self.chartEmbededFigureTwo = FigureCanvas(self.figureTwo)
        self.chartEmbededFigureTwo.setParent(self)  
        self.chartEmbededFigureTwo.setGeometry(int(.05 * width), int(.05 * height) + 115, int(.9 * width), int(height * .75))

        self.figureOne = Figure()
        self.chartEmbededFigureOne = FigureCanvas(self.figureOne)
        self.chartEmbededFigureOne.setParent(self)  
        self.chartEmbededFigureOne.setGeometry(int(.05 * width), int(.05 * height) + 115, int(.9 * width), int(height * .75))

        self.OpenAIAnalysisFigure = QTextEdit(self)
        self.OpenAIAnalysisFigure.setGeometry(int(.05 * width), int(.05 * height) + 115, int(.9 * width), int(height * .75))
        self.OpenAIAnalysisFigure.setStyleSheet('''font-size: 8pt; color: white;
                                                    border-radius: 10px;
                                                    border: 1px solid white;''')
        self.OpenAIAnalysisFigure.setReadOnly(True)

        self.OpenAIAnalysisFigure.hide()
        self.chartEmbededFigureTwo.hide()
        self.chartEmbededFigureOne.hide()
        self.graphLeftButton.hide()
        self.graphRightButton.hide()

    def cycleGraphs(self, factor):

        if(factor == 0):
            self.graphLeftButton.show()
            self.graphRightButton.show()
            self.OpenAIAnalysisFigure.hide()
            self.chartEmbededFigureTwo.hide()
            self.chartEmbededFigureOne.show()
            return

        if (self.chartSlide == 0 and factor == -1) or (self.chartSlide == 2 and factor == 1):
            return
        
        self.chartSlide += factor
        if self.chartSlide == 0:
            self.OpenAIAnalysisFigure.hide()
            self.chartEmbededFigureTwo.hide()
            self.chartEmbededFigureOne.show()
        elif self.chartSlide == 1:
            self.OpenAIAnalysisFigure.hide()
            self.chartEmbededFigureTwo.show()
            self.chartEmbededFigureOne.hide()
        else:
            self.OpenAIAnalysisFigure.show()
            self.chartEmbededFigureTwo.hide()
            self.chartEmbededFigureOne.hide()
    
    def openAIQuery(self, rsi, macd, fib, williams_r, closePriceData, timePeriod):
        
        message = [
            {"role": "user", "content": "You are a technical analyst. You will be given time frame in days, including weekends, technicals in form of a list, with last item being the most recent. Assess if the stock is buy or sell and state rationalle. Assess on the windows of 1 wk, 2 wk, 3 wk, 6 mo, 1 yr, 5 yr."},
        ]
        for name, data in [
            ("RSI",               rsi),
            ("MACD",              macd),
            ("FIBONACCI LEVELS",  fib),
            ("WILLIAMS %R",       williams_r),
            ("CLOSE PRICES",      closePriceData),
            ("TIME RANGE IN DAYS", timePeriod),
        ]:
            message.append({
                "role":    "user",
                "content": f"{name}: {json.dumps(data)}"
            })
        response = self.client.responses.create(model="gpt-4.1", input=message)
        self.OpenAIAnalysisFigure.setPlainText(response.output_text)
        print(response.output_text)

    def initiateSearch(self):

        try:
            ticker = self.tickerSymbolEntry.text().strip().upper()
            timePeriod = int(self.timePeriodDaysEntry.text().strip())
            CurrentDate = datetime.date.today()
            PreviousDate = CurrentDate - datetime.timedelta(days=timePeriod)
            if ticker == "" or not ticker.isalpha() or timePeriod < 30:
                return
        except:
            return
        
        try:
            data = parseDataPolygon(requests.get(f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{PreviousDate.isoformat()}/{CurrentDate.isoformat()}?adjusted=true&sort=asc&limit=50000&apiKey=9cZNiOhwCdE5QpMY8aSsIWh3Z6BVavVC").json()['results'])
            closePriceData, openPriceData, highPriceData, lowPriceData, volumeData = data[1], data[2], data[3], data[4], data[5]
        except:
            return
        
        try:
            currentPrice = int(self.currentPriceEntry.text().strip())
            closePriceData.append(currentPrice)
            highPriceData.append(currentPrice)
            lowPriceData.append(currentPrice)
        except:
            pass
        
        periodRSI = 14
        periodFastMacd = 12
        periodSlowMacd = 26
        signalPeriodMacd = 9
        williamsPeriod = 14

        try:
            rsi = calculateRSI(closePriceData, periodRSI)
            macd = calculateMACD(closePriceData, periodFastMacd, periodSlowMacd, signalPeriodMacd)
            fib = calculateFibonacciRetracements(closePriceData)
            williams_r = calculateWilliamsR(highPriceData, lowPriceData, closePriceData, williamsPeriod)
            self.openAIQuery(rsi, macd, fib, williams_r, closePriceData, timePeriod)
        except Exception as e:
            print(e)
            return

        self.figureOne.clear()
        self.figureTwo.clear()
        self.OpenAIAnalysisFigure.hide()
        axsOne = self.figureOne.subplots(2, 2)
        axsTwo  = self.figureTwo.subplots(2, 2)

        # Plot the Fibonacci Retracements
        axsOne[0, 0].plot(range(len(closePriceData)), closePriceData, label="Price", linewidth=1.5)
        labels = ['0.0%', '23.6%', '38.2%', '50.0%', '61.8%', '78.6%', '100.0%']
        for lvl, label in zip(fib, labels):
            axsOne[0, 0].axhline(y=lvl, linestyle='--', linewidth=1, alpha=0.7)
            axsOne[0, 0].text(len(closePriceData) - 1, lvl, label, va='center', ha='right', fontsize=8)
        axsOne[0, 0].set_title("Fibonacci Retracement")
        axsOne[0, 0].legend()

        # Plot the RSI
        axsOne[1, 0].plot([i + periodRSI + 1 for i in range(len(rsi))], rsi, label=f"RSI: {rsi[-1]}")
        axsOne[1, 0].axhline(70, color='red', linestyle='--')
        axsOne[1, 0].axhline(30, color='green', linestyle='--')
        axsOne[1, 0].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 70, 100, color='red', alpha=0.1)
        axsOne[1, 0].fill_between([i + periodRSI + 1 for i in range(len(rsi))], 0, 30, color='green', alpha=0.1)
        axsOne[1, 0].set_title("RSI")
     
        # Plot the MACD
        axsOne[0, 1].plot([i for i in range(len(macd[0]))], macd[0], color="red", label=f"Signal: {macd[0][-1]}")
        axsOne[0, 1].plot([i for i in range(len(macd[1]))], macd[1], color="green", label=f"MACD: {macd[1][-1]}")
        axsOne[0, 1].set_title("MACD")

        # Plot the Volume
        axsOne[1, 1].plot(range(len(volumeData)), volumeData, label="volume", linewidth=1.5)
        axsOne[1, 1].set_title("Volume")
        axsOne[1, 1].legend()
        
        # Plot the Williams R%
        axsTwo[0, 0].set_ylim(0, -100)
        axsTwo[0, 0].plot(list(range(williamsPeriod-1, williamsPeriod-1 + len(williams_r))), williams_r)
        axsTwo[0, 0].axhline(-20, color='red', linestyle='--')
        axsTwo[0, 0].axhline(-80, color='green', linestyle='--')
        axsTwo[0, 0].fill_between(list(range(williamsPeriod-1, williamsPeriod-1 + len(williams_r))), -20, 0, color='red', alpha=0.1)
        axsTwo[0, 0].fill_between(list(range(williamsPeriod-1, williamsPeriod-1 + len(williams_r))), -80, -100, color='green', alpha=0.1)
        axsTwo[0, 0].set_title("Williams R%")

        # Draw graphs and cycle to first slide
        self.chartEmbededFigureTwo.draw()
        self.chartEmbededFigureOne.draw()
        self.cycleGraphs(0)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow(app.primaryScreen().size().width(), app.primaryScreen().size().height())
    window.show()
    sys.exit(app.exec_())