import tkinter as tk
import tkinter.ttk as ttk
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from bs4 import BeautifulSoup
import numpy as np

class MainApplication:
    def __init__(self, master):
        #Main Window
        self.master = master
        master.title("ASX Data Analysis")
        master.geometry("1280x960")
        master.pack_propagate(False)
        master.resizable(0, 0)
        self.tabBook = ttk.Notebook(master)
        self.tabBook.place(relheight=1, relwidth=1)

        #Tab for Details
        #Frame for Input fields and buttons
        self.inputFrame = ttk.LabelFrame(self.tabBook, text="User Input")
        self.inputFrame.place(width=1280) 
        self.tabBook.add(self.inputFrame, text="Details")
        # Lables
        self.ASXLabel = tk.Label(self.inputFrame, text="ASX ticker")
        self.ASXLabel.grid(row=0, column=1)
        self.tickerEntry = tk.Entry(self.inputFrame, width=20)
        self.tickerEntry.grid(row=0, column=0)
        #Buttons
        self.trendButton = ttk.Button(self.inputFrame, text='Plot Stock Price', width=20, command=self.plotTrends)
        self.trendButton.grid(row=1, column=0)
        self.stockButton = ttk.Button(self.inputFrame, text='Update Data', width=20, command=self.getDetails)
        self.stockButton.grid(row=2, column=0)
        self.quitButton = ttk.Button(self.inputFrame, text='Quit', width=10, command=self.master.destroy)
        self.quitButton.place(relx=0.9)

        # Frame for Treeview (info)
        self.infoFrame = ttk.LabelFrame(self.tabBook, text="Stock Summary")
        self.infoFrame.place(height=370, width=640, rely=0.12)
        #Treeview widget
        self.infoTv = ttk.Treeview(self.infoFrame)
        self.infoTv.place(relheight=1, relwidth=1)
        self.treescrolly = ttk.Scrollbar(self.infoFrame, orient="vertical", command=self.infoTv.yview)
        self.treescrollx = ttk.Scrollbar(self.infoFrame, orient="horizontal", command=self.infoTv.xview)
        self.infoTv.configure(xscrollcommand=self.treescrollx.set, yscrollcommand=self.treescrolly.set)
        self.treescrollx.pack(side="bottom", fill="x")
        self.treescrolly.pack(side="right", fill="y")
        #Define and format columns
        self.infoTv["columns"] = ("Item", "Value")
        self.infoTv.column("#0", width=0, stretch=False)
        self.infoTv.column("Item")
        self.infoTv.column("Value")
        #Create headings
        self.infoTv.heading("#0", text="")
        self.infoTv.heading("Item", text="Item", anchor="w")
        self.infoTv.heading("Value", text="Value", anchor="w")

        #Frame for Estimates (calculations)
        self.estimateFrame = ttk.LabelFrame(self.tabBook, text="Estimated forward values")
        self.estimateFrame.place(height=370, width=640, rely=0.12, relx=0.5)
        #Calc button
        self.calcButton = ttk.Button(self.estimateFrame, text='Calculate Estimates', width=20, command=self.runEstimate) #add command to update text of calc labels
        self.calcButton.grid(row=0, column=2)
        #Entry fields
        self.ebitdaLabel = tk.Label(self.estimateFrame, width=20, text="EBITDA ($M)", anchor="w")
        self.ebitdaLabel.grid(row=0, column=0)
        self.ebitdaEntry = tk.Entry(self.estimateFrame, width=20)
        self.ebitdaEntry.grid(row=0, column=1)
        self.sharesOutstandingLabel = tk.Label(self.estimateFrame, width=20, text="Shares Outstanding (M)", anchor="w")
        self.sharesOutstandingLabel.grid(row=1, column=0)
        self.sharesOutstandingEntry = tk.Entry(self.estimateFrame, width=20)
        self.sharesOutstandingEntry.grid(row=1, column=1)
        self.longDebtLabel = tk.Label(self.estimateFrame, width=20, text="L/T Debt ($M)", anchor="w")
        self.longDebtLabel.grid(row=2, column=0)
        self.longDebtEntry = tk.Entry(self.estimateFrame, width=20)
        self.longDebtEntry.grid(row=2, column=1)
        self.cashLabel = tk.Label(self.estimateFrame, width=20, text="Cash on hand ($M)", anchor="w")
        self.cashLabel.grid(row=3, column=0)
        self.cashEntry = tk.Entry(self.estimateFrame, width=20)
        self.cashEntry.grid(row=3, column=1)
        self.percentEbitdaLabel = tk.Label(self.estimateFrame, width=20, text="% EBITDA", anchor="w")
        self.percentEbitdaLabel.grid(row=4, column=0)
        self.percentEbitdaEntry = tk.Entry(self.estimateFrame, width=20)
        self.percentEbitdaEntry.grid(row=4, column=1)
        self.blankspacer = tk.Label(self.estimateFrame, width=20)
        self.blankspacer.grid(row=5, column=0)
        #Calculated values
        self.medianPriceLabel = tk.Label(self.estimateFrame, width=20, text="Median Price", anchor="w")
        self.medianPriceLabel.grid(row=6, column=0)
        self.medianPriceCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.medianPriceCalc.grid(row=6, column=1)
        self.averagePriceLabel = tk.Label(self.estimateFrame, width=20, text="Average Price", anchor="w")
        self.averagePriceLabel.grid(row=7, column=0)
        self.averagePriceCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.averagePriceCalc.grid(row=7, column=1)
        self.minPriceLabel = tk.Label(self.estimateFrame, width=20, text="Minimum Price", anchor="w")
        self.minPriceLabel.grid(row=8, column=0)
        self.minPriceCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.minPriceCalc.grid(row=8, column=1)
        self.maxPriceLabel = tk.Label(self.estimateFrame, width=20, text="Maximum Price", anchor="w")
        self.maxPriceLabel.grid(row=9, column=0)
        self.maxPriceCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.maxPriceCalc.grid(row=9, column=1)
        self.divPaidLabel = tk.Label(self.estimateFrame, width=20, text="Dividends Paid ($M)", anchor="w")
        self.divPaidLabel.grid(row=10, column=0)
        self.divPaidCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.divPaidCalc.grid(row=10, column=1)
        self.medianYieldLabel = tk.Label(self.estimateFrame, width=20, text="Median Yield", anchor="w")
        self.medianYieldLabel.grid(row=11, column=0)
        self.medianYieldCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.medianYieldCalc.grid(row=11, column=1)
        self.averageYieldLabel = tk.Label(self.estimateFrame, width=20, text="Average Yield", anchor="w")
        self.averageYieldLabel.grid(row=12, column=0)
        self.averageYieldCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.averageYieldCalc.grid(row=12, column=1)
        self.minYieldLabel = tk.Label(self.estimateFrame, width=20, text="Minimum Yield", anchor="w")
        self.minYieldLabel.grid(row=13, column=0)
        self.minYieldCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.minYieldCalc.grid(row=13, column=1)
        self.maxYieldLabel = tk.Label(self.estimateFrame, width=20, text="Maximum Yield", anchor="w")
        self.maxYieldLabel.grid(row=14, column=0)
        self.maxYieldCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.maxYieldCalc.grid(row=14, column=1)
        self.assessedDivLabel = tk.Label(self.estimateFrame, width=20, text="Assessed Dividend", anchor="w")
        self.assessedDivLabel.grid(row=15, column=0)
        self.assessedDivCalc = tk.Label(self.estimateFrame, width=20, anchor="w")
        self.assessedDivCalc.grid(row=15, column=1)
        #averaged values
        self.cashYieldLabel = tk.Label(self.estimateFrame, width=10, text="Cash Yield")
        self.cashYieldLabel.grid(row=5, column=3)
        self.evLabel = tk.Label(self.estimateFrame, width=10, text="EV Multiple")
        self.evLabel.grid(row=5, column=4)

        self.medianValueLabel = tk.Label(self.estimateFrame, width=10, text="Median Value", anchor="w")
        self.medianValueLabel.grid(row=6, column=2)
        self.medianValueCashCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.medianValueCashCalc.grid(row=6, column=3)
        self.medianValueEvCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.medianValueEvCalc.grid(row=6, column=4)
        self.meanValueLabel = tk.Label(self.estimateFrame, width=10, text="Mean Value", anchor="w")
        self.meanValueLabel.grid(row=7, column=2)
        self.meanValueCashCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.meanValueCashCalc.grid(row=7, column=3)
        self.meanValueEvCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.meanValueEvCalc.grid(row=7, column=4)
        self.stdValueLabel = tk.Label(self.estimateFrame, width=10, text="Std. Dev.", anchor="w")
        self.stdValueLabel.grid(row=8, column=2)
        self.stdValueCashCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.stdValueCashCalc.grid(row=8, column=3)
        self.stdValueEvCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.stdValueEvCalc.grid(row=8, column=4)
        self.minValueLabel = tk.Label(self.estimateFrame, width=10, text="Min. value", anchor="w")
        self.minValueLabel.grid(row=9, column=2)
        self.minValueCashCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.minValueCashCalc.grid(row=9, column=3)
        self.minValueEvCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.minValueEvCalc.grid(row=9, column=4)
        self.maxValueLabel = tk.Label(self.estimateFrame, width=10, text="Max. value", anchor="w")
        self.maxValueLabel.grid(row=10, column=2)
        self.maxValueCashCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.maxValueCashCalc.grid(row=10, column=3)
        self.maxValueEvCalc = tk.Label(self.estimateFrame, width=10, anchor="w")
        self.maxValueEvCalc.grid(row=10, column=4)

        #Frame for KPIs (Selected info from database)
        self.keyPerformanceFrame = ttk.LabelFrame(self.tabBook, text="Key Performance Indicators")
        self.keyPerformanceFrame.place(height=165, width=1280, rely=0.5)
        #Treeview widget
        self.keyPerformanceTv = ttk.Treeview(self.keyPerformanceFrame)
        self.keyPerformanceTv.place(relheight=1, relwidth=1)
        self.dtreescrolly = ttk.Scrollbar(self.keyPerformanceFrame, orient="vertical", command=self.keyPerformanceTv.yview)
        self.dtreescrollx = ttk.Scrollbar(self.keyPerformanceFrame, orient="horizontal", command=self.keyPerformanceTv.xview)
        self.keyPerformanceTv.configure(xscrollcommand=self.dtreescrollx.set, yscrollcommand=self.dtreescrolly.set)
        self.dtreescrollx.pack(side="bottom", fill="x")
        self.dtreescrolly.pack(side="right", fill="y")
        #Define and format columns
        self.keyPerformanceTv["columns"] = ("Item", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019")
        self.keyPerformanceTv.column("#0", width=0, stretch=False)
        for column in self.keyPerformanceTv["columns"]:
            self.keyPerformanceTv.column(column, width=50)
        self.keyPerformanceTv.column("Item", width=250)
        #Create headings
        self.keyPerformanceTv.heading("#0", text="")
        for column in self.keyPerformanceTv["columns"]:
            self.keyPerformanceTv.heading(column, text=column, anchor="w")

        #Frame for Details (Extended info from database)
        self.detailsFrame = ttk.LabelFrame(self.tabBook, text="Historical Performance")
        self.detailsFrame.place(height=300, width=1280, rely=0.67)
        #Treeview widget
        self.detailTv = ttk.Treeview(self.detailsFrame)
        self.detailTv.place(relheight=1, relwidth=1)
        self.dtreescrolly = ttk.Scrollbar(self.detailsFrame, orient="vertical", command=self.detailTv.yview)
        self.dtreescrollx = ttk.Scrollbar(self.detailsFrame, orient="horizontal", command=self.detailTv.xview)
        self.detailTv.configure(xscrollcommand=self.dtreescrollx.set, yscrollcommand=self.dtreescrolly.set)
        self.dtreescrollx.pack(side="bottom", fill="x")
        self.dtreescrolly.pack(side="right", fill="y")
        #Define and format columns
        self.detailTv["columns"] = ("Item", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019")
        self.detailTv.column("#0", width=0, stretch=False)
        for column in self.detailTv["columns"]:
            self.detailTv.column(column, width=50)
        self.detailTv.column("Item", width=250)
        #Create headings
        self.detailTv.heading("#0", text="")
        for column in self.detailTv["columns"]:
            self.detailTv.heading(column, text=column, anchor="w")

        #Tab for Trend Plots
        self.trendsFrame = ttk.LabelFrame(self.tabBook, text="Plots")
        self.trendsFrame.place(relheight=1, relwidth=1)
        self.tabBook.add(self.trendsFrame, text="Plots")

        #Tab for Screening Tool
        self.screenFrame = ttk.LabelFrame(self.tabBook, text="Screening Tool")
        self.screenFrame.place(relheight=1, relwidth=1)
        self.tabBook.add(self.screenFrame, text="Screening Tool")

    def runEstimate(self):
        ebitda = float(self.ebitdaEntry.get())
        sharesOutstanding = float(self.sharesOutstandingEntry.get())
        longDebt = float(self.longDebtEntry.get())
        cashOnHand = float(self.cashEntry.get())
        percentEbitda = float(self.percentEbitdaEntry.get())

        # self.medianPriceCalc.config(text=(ebitda*sharesOutstanding-longDebt+cashOnHand)/sharesOutstanding)
        # self.averagePriceCalc.config(text=(ebitda*sharesOutstanding-longDebt+cashOnHand)/sharesOutstanding)

    def plotTrends(self):
        sheetDict = {'historical price - max': '1d', 'historical price - 5y': '1d', 'historical price - 1y': '1d', 'historical price - 6mo': '1d', 'historical price - 3mo': '1d', 'historical price - 1mo': '1d', 'historical price - 5d': '60m', 'historical price - 1d': '1m'}    
        try:
            #Plot trend data for all time periods
            trends = plt.figure()
            trends.subplots_adjust(wspace=0.2, hspace=0.5)
            plotpos = 1
            for sheet in sheetDict.keys():   
                sheetDict[sheet] = yf.download(self.tickerEntry.get()+'.AX', period=sheet.split("- ")[1], interval=sheetDict[sheet])   
                trends.add_subplot(4, 2, plotpos, title=f"{self.tickerEntry.get()} - {sheet}", ylabel="$AUD").plot(sheetDict[sheet]['Close'])
                plotpos += 1      
            #Add to tinker GUI
            chart = FigureCanvasTkAgg(trends, self.trendsFrame)
            chart.get_tk_widget().place(relheight=1, relwidth=1)
        except:
            print(f"Something went wrong retrieving {self.tickerEntry.get()} historical data")
            print('Press enter to close...')
            input()
            sys.exit()

    def getDetails(self):
        #Get History
        try:
            database = pd.read_csv(os.getcwd() + '\\data\\database.csv') 
            countd = 0
            keyPerformanceIndicators = ['EBITDA', 'L/T Debt', 'Market cap ', 'Cash on hand', 'Dividends (¢)', 'Shares outstanding ', 'S/T debt']
            keyPerformanceIndicatorDict = {}
            keywords = ['EBITDA',
                    'EBIT',
                    'L/T Debt',
                    'S/T debt',
                    'Market cap ',
                    'Dividends (¢)',
                    'Dividend yield (%)',
                    'Revenues ',
                    'Net profit ',
                    'Net profit margin(%)',
                    'Capital spending (¢)',
                    'Cash on hand',
                    'Net operating cashflows ',
                    'Net investing cashflows ',
                    'Net financing cashflows ',
                    'Cash flow (¢)',
                    'Earnings pre abs (¢)',
                    'Book value ($)',
                    'Average annual P/E ratio (%)',
                    'Relative P/E (%)',
                    'Total return (%)',
                    'Depreciation ',
                    'Amortisation ',
                    'Income tax rate (%)',
                    'Employees (thousands)',
                    'Shareholders equity',
                    'Return on capital (%)',
                    'Return on equity (%)',
                    'Payout ratio (%)',
                    'Shares outstanding ']
            for row in database.to_numpy():
                if self.tickerEntry.get() in row[0]:
                    for keyword in keywords:
                        if self.tickerEntry.get() + " " + keyword == row[0]:
                            self.detailTv.insert(parent="", index="end", iid=countd, text="", values=[value for value in row])
                            #check for KPI treeview
                            if keyword in keyPerformanceIndicators:
                                keyPerformanceIndicatorDict[keyword] = np.array(list(row)[1:]).astype(float)
                            countd += 1
        except:
            print(f"Something went wrong getting historical data for {self.tickerEntry.get()}!")
            input()
            sys.exit()

        # Calculate KPIs
        try:
            keyPerformanceIndicatorList = []
            cashYieldList = ['EBITDA', 'L/T Debt', 'Market cap ']
            eVMultipleList = ['L/T Debt', 'Market cap ', 'Cash on hand']
            dividendsPaidList = ['Dividends (¢)', 'Shares outstanding ']
            percentEbitdaList = ['Dividends (¢)', 'Shares outstanding ', 'EBITDA']
            netDebtRatioList = ['L/T Debt', 'S/T debt', 'Cash on hand', 'EBITDA']

            if all(item in keyPerformanceIndicatorDict for item in cashYieldList):
                keyPerformanceIndicatorList.append(['Cash Yield'] + list(np.round(keyPerformanceIndicatorDict['EBITDA'] / (keyPerformanceIndicatorDict['L/T Debt'] + keyPerformanceIndicatorDict['Market cap ']) * 100, 2)))
            if all(item in keyPerformanceIndicatorDict for item in eVMultipleList):
                keyPerformanceIndicatorList.append(['EV Multiple'] + list(np.round((keyPerformanceIndicatorDict['L/T Debt'] + keyPerformanceIndicatorDict['Market cap '] - keyPerformanceIndicatorDict['Cash on hand']) / keyPerformanceIndicatorDict['EBITDA'], 1)))
            if all(item in keyPerformanceIndicatorDict for item in dividendsPaidList):
                keyPerformanceIndicatorList.append(['Dividends paid ($M)'] + list(np.round(keyPerformanceIndicatorDict['Dividends (¢)'] * keyPerformanceIndicatorDict['Shares outstanding '] / 100, 1)))
            if all(item in keyPerformanceIndicatorDict for item in percentEbitdaList):
                keyPerformanceIndicatorList.append(['% EBDITA'] + list(np.round((keyPerformanceIndicatorDict['Dividends (¢)'] * keyPerformanceIndicatorDict['Shares outstanding '] / 100) / keyPerformanceIndicatorDict['EBITDA'] * 100, 0)))
            if all(item in keyPerformanceIndicatorDict for item in netDebtRatioList):
                keyPerformanceIndicatorList.append(['Net Debt : EBITDA'] + list(np.round((keyPerformanceIndicatorDict['L/T Debt'] + keyPerformanceIndicatorDict['S/T debt'] - keyPerformanceIndicatorDict['Cash on hand']) / keyPerformanceIndicatorDict['EBITDA'], 1)))
            
            print(keyPerformanceIndicatorList)

            countk = 0
            for kpi in keyPerformanceIndicatorList:
                self.keyPerformanceTv.insert(parent="", index="end", iid=countk, text="", values=[value for value in kpi])
                countk += 1
        except:
            print(f"Something went wrong getting KPIs for {self.tickerEntry.get()}!")
            input()
            sys.exit()

        # initialise driver
        print("....LOADING: Starting Web Driver...")
        options = Options()
        options.headless = True
        geckodriver = os.getcwd() + '\\geckodriver.exe'
        # geckodriver = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'geckodriver.exe'))
        driver = webdriver.Firefox(executable_path=geckodriver, options=options)
        extensionDirectory = os.getcwd() + '\\driver_extensions\\'
        # extensionDirectory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'driver_extensions'))
        extensions = [
            '\\https-everywhere@eff.org.xpi',
            '\\uBlock0@raymondhill.net.xpi',
        ]
        for extension in extensions:
            driver.install_addon(extensionDirectory + extension, temporary=True)
        
        #Get ticker info
        try:
            driver.get(f"https://www.morningstar.com.au/Stocks/NewsAndQuotes/{self.tickerEntry.get()}")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
        except:
            print(f"Something went wrong loading the {self.tickerEntry.get()} morning star page!")
            driver.quit()
            print('Press enter to close...')
            input()
            sys.exit()
        try:
            html = driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            detailDictionary = {}
            detailDictionary['Name'] = driver.find_element_by_xpath("//h1[contains(@class, 'N_QHeader_b')]/label").text
            detailDictionary['Value'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[1]/span/span[2]").text
            detailDictionary['Day change cents'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[2]/div[2]/span[1]").text
            detailDictionary['Day change percent'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[2]/div[2]/span[3]").text
            asOfText = tk.Label(self.inputFrame, text=driver.find_element_by_class_name("N_QText").text) 
            asOfText.grid(row=2, column=2)
            for item in soup.findAll('td'):
                if item.find('span') and item.find('h3'):
                    detailDictionary[item.find('h3').text] = item.find('span').text
            if detailDictionary['\xa0Company Profile']:
                del detailDictionary['\xa0Company Profile']
            detailDictionary['Market Cap'].replace("\xa0", "").replace(",", "").replace("M", "000000").replace("B", "000000000")
            #Populate Tkinter treeview
            count = 0
            for item in detailDictionary:
                self.infoTv.insert(parent="", index="end", iid=count, text="", values=(item, detailDictionary[item]))
                count += 1
            #stop driver
            driver.quit()
        except:
            print(f"Something went wrong scraping {self.tickerEntry.get()} info!")
            driver.quit()
            input()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()