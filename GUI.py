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
import statistics
from criteriawidget import *
from tvwidget import *
from calcinput import *
from calcoutput import *
from statoutput import *
from screen import *

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
        #Lables
        tk.Label(self.inputFrame, text="ASX ticker", width=20, anchor="w").grid(row=0, column=1)
        self.tickerEntry = tk.Entry(self.inputFrame, width=20)
        self.tickerEntry.grid(row=0, column=0)
        #Buttons
        ttk.Button(self.inputFrame, text='Show Data for listing', width=20, command=self.printDetailsTv).grid(row=2, column=0)
        ttk.Button(self.inputFrame, text='Refresh Daily Data', width=20, command=self.getDailyDetails).grid(row=3, column=0)
        ttk.Button(self.inputFrame, text='Quit', width=10, command=self.master.destroy).place(relx=0.9)

        # Frame for Treeview (info)
        self.infoFrame = ttk.LabelFrame(self.tabBook, text="Stock Summary")
        self.infoFrame.place(height=370, width=640, rely=0.12)
        #Treeview widget
        self.infoTv = tvwidget(frame=self.infoFrame, relheight=1, relwidth=1, columns=("Item", "Value"))

        #Frame for Estimates (calculations)
        self.estimateFrame = ttk.LabelFrame(self.tabBook, text="Estimated forward values")
        self.estimateFrame.place(height=370, width=640, rely=0.12, relx=0.5)
        #Calc button
        ttk.Button(self.estimateFrame, text='Calculate Estimates', width=20, command=self.runEstimate).grid(row=0, column=2)
        #Entry fields
        self.ebitdaEntry = calcinput(self.estimateFrame, text="EBITDA ($M)", row=0, col=0)
        self.sharesOutstandingEntry = calcinput(self.estimateFrame, text="Shares Outstanding (M)", row=1, col=0)
        self.longDebtEntry = calcinput(self.estimateFrame, text="L/T Debt ($M)", row=2, col=0)
        self.cashEntry = calcinput(self.estimateFrame, text="Cash on hand ($M)", row=3, col=0)
        self.percentEbitdaEntry = calcinput(self.estimateFrame, text="% EBITDA", row=4, col=0)
        tk.Label(self.estimateFrame, width=20).grid(row=5, column=0)

        #Calculated values
        self.medianPriceCalc = calcoutput(self.estimateFrame, text="Median Price", row=6, col=0, width=20)
        self.averagePriceCalc = calcoutput(self.estimateFrame, text="Average Price", row=7, col=0, width=20)
        self.minPriceCalc = calcoutput(self.estimateFrame, text="Min Price", row=8, col=0, width=20)
        self.maxPriceCalc = calcoutput(self.estimateFrame, text="Max Price", row=9, col=0, width=20)
        self.divPaidCalc = calcoutput(self.estimateFrame, text="Dividends Paid ($M)", row=10, col=0, width=20)
        self.medianYieldCalc = calcoutput(self.estimateFrame, text="Median Yield", row=11, col=0, width=20)
        self.averageYieldCalc = calcoutput(self.estimateFrame, text="Average Yield", row=12, col=0, width=20)
        self.minYieldCalc = calcoutput(self.estimateFrame, text="Minimum Yield", row=13, col=0, width=20)
        self.maxYieldCalc = calcoutput(self.estimateFrame, text="Maximum Yield", row=14, col=0, width=20)
        self.assessedDivCalc = calcoutput(self.estimateFrame, text="Assessed Dividend", row=15, col=0, width=20)

        #stats values
        tk.Label(self.estimateFrame, width=10, text="Cash Yield %").grid(row=5, column=3)
        tk.Label(self.estimateFrame, width=10, text="EV Multiple").grid(row=5, column=4)
        self.medianValueCalc = statoutput(self.estimateFrame, text="Median Value", row=6, col=2, width=10)
        self.meanValueCalc = statoutput(self.estimateFrame, text="Mean Value", row=7, col=2, width=10)
        self.stdValueCalc = statoutput(self.estimateFrame, text="Std. Dev.", row=8, col=2, width=10)
        self.minValueCalc = statoutput(self.estimateFrame, text="Min. value", row=9, col=2, width=10)
        self.maxValueCalc = statoutput(self.estimateFrame, text="Max. value", row=10, col=2, width=10)

        #Frame for KPIs (Selected info from database)
        self.keyPerformanceFrame = ttk.LabelFrame(self.tabBook, text="Key Performance Indicators")
        self.keyPerformanceFrame.place(height=165, width=1280, rely=0.5)
        #Treeview widget
        self.keyPerformanceTv = tvwidget(frame=self.keyPerformanceFrame, relheight=1, relwidth=1, columns=("Item", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"), firstColWidth=250, colWidth=50)

        #Frame for Details (Extended info from database)
        self.detailsFrame = ttk.LabelFrame(self.tabBook, text="Historical Performance")
        self.detailsFrame.place(height=300, width=1280, rely=0.67)
        #Treeview widget
        self.detailTv = tvwidget(frame=self.detailsFrame, relheight=1, relwidth=1, columns=("Item", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"), firstColWidth=250, colWidth=50)

        #Tab for Trend Plots
        self.trendsFrame = ttk.LabelFrame(self.tabBook, text="Plots")
        self.trendsFrame.place(relheight=1, relwidth=1)
        self.tabBook.add(self.trendsFrame, text="Plots")
        ttk.Button(self.trendsFrame, text='Plot Stock Price', width=20, command=self.plotTrends).grid(row=1, column=0)
        ttk.Button(self.trendsFrame, text='Quit', width=10, command=self.master.destroy).place(relx=0.9)

        #Tab for Screening Tool
        self.screenFrame = ttk.LabelFrame(self.tabBook, text="Screening Tool")
        self.screenFrame.place(relheight=1, relwidth=1)
        self.tabBook.add(self.screenFrame, text="Screening Tool")
        tk.Label(self.screenFrame, width=20).grid(row=12, column=0)
        ttk.Button(self.screenFrame, text='Search', width=20, command=self.screen).grid(row=13, column=0)
        ttk.Button(self.screenFrame, text='Quit', width=10, command=self.master.destroy).place(relx=0.9)
        self.search = tk.IntVar()
        tk.Radiobutton(self.screenFrame, text="Most recent year only", variable=self.search, value=1, anchor="w", width=20).grid(row=13, column=3)
        tk.Radiobutton(self.screenFrame, text="Average from 2010", variable=self.search, value=2, anchor="w", width=20).grid(row=14, column=3)
        self.sectors = [
            "All",
            "All",
            "Automobiles & Components",
            "Banks",
            "Capital Goods",
            "Class Pend",
            "Commerical & Professional Services",
            "Consumer Durables & Apparel",
            "Consumer Services",
            "Diversified Financials",
            "Energy",
            "Food & Staples Retailing",
            "Food, Beverage & Tobacco",
            "Health Care Equipment & Services",
            "Household & Personal Products",
            "Insurance",
            "Materials",
            "Media & Entertainment",
            "Not Applic",
            "Pharmaceuticals, Biotechnology & Life Sciences",
            "Real Estate",
            "Retailing",
            "Semiconductors & Semiconductor Equipment",
            "Software & Services",
            "Technology Hardware & Equipment",
            "Telecommunication Services",
            "Transportation",
            "Utilities"
            ]
        self.sector = tk.StringVar(self.screenFrame)
        self.sector.set("All")
        tk.Label(self.screenFrame, text="Sector/Industry", width=20, anchor="w").grid(row=13, column=6)
        ttk.OptionMenu(self.screenFrame, self.sector, *self.sectors).grid(row=13, column=7)

        #Entry fields for screening tool 
        self.marketCapCriteria = criteriawidget(self.screenFrame, "Market Capital ($M)", 0, 0)
        self.sharesOutstandingCriteria = criteriawidget(self.screenFrame, "Shares Outstanding (mil)", 4, 0)
        self.shortDebtCriteria = criteriawidget(self.screenFrame, "Short-term debt ($M)", 8, 0)
        self.dividendsCriteria = criteriawidget(self.screenFrame, "Dividends (c)", 0, 3)
        self.dividendYieldCriteria = criteriawidget(self.screenFrame, "Dividend yield (%)", 4, 3)
        self.ebitdaCriteria = criteriawidget(self.screenFrame, "EBITDA (%)", 8, 3)
        self.cashYieldCriteria = criteriawidget(self.screenFrame, "Cash yield (%)", 0, 6)
        self.cashCriteria = criteriawidget(self.screenFrame, "Cash on hand ($M)", 4, 6)
        self.longDebtCriteria = criteriawidget(self.screenFrame, "Long-term debt ($M)", 8, 6)
        self.bookValueCriteria = criteriawidget(self.screenFrame, "Book value ($)", 0, 9)
        self.evMultipleCriteria = criteriawidget(self.screenFrame, "EV Multiple", 4, 9)
        self.returnCapitalCriteria = criteriawidget(self.screenFrame, "Return on capital (%)", 8, 9)
        self.priceEarningsCriteria = criteriawidget(self.screenFrame, "Price/Earnings (%)", 0, 12)
        self.profitMarginCriteria = criteriawidget(self.screenFrame, "Profit Margin(%)", 4, 12)
        self.netDebtEbitdaRatioCriteria = criteriawidget(self.screenFrame, "Net debt : EBITDA (ratio)", 8, 12)

        #Screening tool output frame
        self.screenOutput = ttk.LabelFrame(self.screenFrame, text="Search Results")
        self.screenOutput.place(height=650, width=1280, rely=0.28)

        #Screening tool Output treeview
        columns = (
            "Name", 
            "Ticker", 
            "Sector", 
            "EV Multiple", 
            "Cash yield (%)", 
            "Net debt : EBITDA (ratio)", 
            "Market capital ($M)", 
            "Dividends (c)", 
            "Dividend yield (%)", 
            "Book value ($)", 
            "Price / Earnings (%)", 
            "Shares Outstanding (mil)", 
            "Cash on hand ($M)", 
            "Profit margin (%)", 
            "Short-term debt ($M)", 
            "EBITDA ($M)", 
            "Return on captial (%)", 
            "Long-term debt ($M)"
            )
        self.screenTv = tvwidget(self.screenOutput, 1, 1, columns, 250, 150)
    
    def listOperation(self, operation, list1, list2):
        if operation == "sum":
            return [round(a + b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "mul":
            return [round(a * b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "sub":
            return [round(a - b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "div":
            return [round(a / b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        
    def runEstimate(self):
        self.medianPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.medianValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry())/self.sharesOutstandingEntry.getEntry())
        self.averagePriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.meanValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry())/self.sharesOutstandingEntry.getEntry())
        self.minPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.minValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry())/self.sharesOutstandingEntry.getEntry())
        self.maxPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.maxValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry())/self.sharesOutstandingEntry.getEntry())
        self.divPaidCalc.changeText(text=self.ebitdaEntry.getEntry()*self.percentEbitdaEntry.getEntry()/100)

        self.assessedDivCalc.changeText(text=100*self.divPaidCalc.getValue()/self.sharesOutstandingEntry.getEntry())
        self.medianYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.medianPriceCalc.getValue(), 2)} %")
        self.averageYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.averagePriceCalc.getValue(), 2)} %")
        self.minYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.minPriceCalc.getValue(), 2)} %")
        self.maxYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.maxPriceCalc.getValue(), 2)} %")

    def plotTrends(self):
        sheetDict = {
            'historical price - max': '1d',
            'historical price - 5y': '1d',
            'historical price - 1y': '1d',
            'historical price - 6mo': '1d',
            'historical price - 3mo': '1d',
            'historical price - 1mo': '1d',
            'historical price - 5d': '60m',
            'historical price - 1d': '1m'
            }    
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
            chart.get_tk_widget().place(relheight=0.95, relwidth=1, rely=0.05)
        except:
            print(f"Something went wrong retrieving {self.tickerEntry.get()} historical data")
            print('Press enter to close...')
            input()
            sys.exit()

    def convertDictToList(self, dictionary):
        detailList = []
        for key, value in dictionary.items():
            temp = [key] + list(value)
            detailList.append(temp)
        return detailList

    def getDetails(self, ticker):
        #Get History
        database = pd.read_csv(os.getcwd() + '\\data\\database.csv') 
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
        detailDict = {}
        for row in database.to_numpy():
            if ticker in row[0]:
                for keyword in keywords:
                    if ticker + " " + keyword == row[0]:
                        valueList = []
                        for value in list(row)[1:]:
                            if value != "—":
                                value = float(value)
                            valueList.append(value)
                        detailDict[keyword] = np.array(valueList)
        return detailDict
    
    def printDetailsTv(self):
        detailList = self.convertDictToList(self.getDetails(self.tickerEntry.get()))
        for count, row in enumerate(detailList):
            self.detailTv.insertValues([value for value in row], count)

        keyDetailList = self.convertDictToList(self.getKeyDetails(self.tickerEntry.get()))
        for count, row in enumerate(keyDetailList):
                self.keyPerformanceTv.insertValues([value for value in row], count)
    
    def statCalc(self, statistic, list):
        if statistic == "median":
            try:
                return np.round(statistics.median(list), 1)
            except:
                return "—"
        if statistic == "mean":
            try:
                return np.round(statistics.mean(list), 1)
            except:
                return "—"
        if statistic == "stdev":
            try:
                return np.round(statistics.stdev(list), 1)
            except:
                return "—"
        if statistic == "min":
            try:
                return np.round(statistics.stdev(list) - statistics.mean(list), 1)
            except:
                return "—"
        if statistic == "max":
            try:
                return np.round(statistics.stdev(list) + statistics.mean(list), 1)
            except:
                return "—"


    def getKeyDetails(self, ticker):
        detailList = self.convertDictToList(self.getDetails(ticker))
        keyDetailDict = {}
        kpiList = ['EBITDA', 'L/T Debt', 'Market cap ', 'Cash on hand', 'Dividends (¢)', 'Shares outstanding ', 'S/T debt']
        #check for KPI treeview
        for row in detailList:
            if row[0] in kpiList:
                valueList = []
                for value in list(row)[1:]:
                    if value != "—":
                        value = float(value)
                    valueList.append(value)
                keyDetailDict[row[0]] = np.array(valueList)
        
        cashYieldList = ['EBITDA', 'L/T Debt', 'Market cap ']
        evMultipleList = ['L/T Debt', 'Market cap ', 'Cash on hand']
        dividendsPaidList = ['Dividends (¢)', 'Shares outstanding ']
        percentEbitdaList = ['Dividends (¢)', 'Shares outstanding ', 'EBITDA']
        netDebtRatioList = ['L/T Debt', 'S/T debt', 'Cash on hand', 'EBITDA']
        
        if all(item in keyDetailDict for item in cashYieldList):
            cashYields = [round(ele * 100, 2) if isinstance(ele, float) else "—" for ele in list(self.listOperation("div", keyDetailDict['EBITDA'], self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap '])))]
            keyDetailDict['Cash Yield'] = cashYields
            self.medianValueCalc.changeCashYield(text=self.statCalc("median", [ele for ele in cashYields if isinstance(ele, float)]))
            self.meanValueCalc.changeCashYield(text=self.statCalc("mean", [ele for ele in cashYields if isinstance(ele, float)]))
            self.stdValueCalc.changeCashYield(text=self.statCalc("stdev", [ele for ele in cashYields if isinstance(ele, float)]))
            self.minValueCalc.changeCashYield(text=self.statCalc("min", [ele for ele in cashYields if isinstance(ele, float)]))
            self.maxValueCalc.changeCashYield(text=self.statCalc("max", [ele for ele in cashYields if isinstance(ele, float)]))
        else:
            keyDetailDict['Cash Yield'] = "—"
        if all(item in keyDetailDict for item in evMultipleList):
            evMultiples = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap ']), keyDetailDict['Cash on hand']), keyDetailDict['EBITDA'])
            keyDetailDict['EV Multiple'] = evMultiples
            self.medianValueCalc.changeEvValue(text=self.statCalc("median", [ele for ele in evMultiples if isinstance(ele, float)]))
            self.meanValueCalc.changeEvValue(text=self.statCalc("mean", [ele for ele in evMultiples if isinstance(ele, float)]))
            self.stdValueCalc.changeEvValue(text=self.statCalc("stdev", [ele for ele in evMultiples if isinstance(ele, float)]))
            self.minValueCalc.changeEvValue(text=self.statCalc("min", [ele for ele in evMultiples if isinstance(ele, float)]))
            self.maxValueCalc.changeEvValue(text=self.statCalc("max", [ele for ele in evMultiples if isinstance(ele, float)]))
        else:
            keyDetailDict['EV Multiple'] = "—"
        if all(item in keyDetailDict for item in dividendsPaidList):
            keyDetailDict['Dividends paid ($M)'] = [round(ele / 100, 2) if isinstance(ele, float) else "—" for ele in list(self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding ']))]
        else:
            keyDetailDict['Dividends paid ($M)'] = "—"
        if all(item in keyDetailDict for item in percentEbitdaList):
            keyDetailDict['% EBDITA'] = self.listOperation("div", self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding ']), keyDetailDict['EBITDA'])
        else:
            keyDetailDict['% EBDITA'] = "—"
        if all(item in keyDetailDict for item in netDebtRatioList):
            keyDetailDict['Net Debt : EBITDA'] = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['S/T debt']), keyDetailDict['Cash on hand']), keyDetailDict['EBITDA'])
        else:
            keyDetailDict['Net Debt : EBITDA'] = "—"

        return keyDetailDict

    def getDailyDetails(self):
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
            for i, item in enumerate(detailDictionary):
                self.infoTv.insertValues((item, detailDictionary[item]), i)
            #stop driver
            driver.quit()
        except:
            print(f"Something went wrong scraping {self.tickerEntry.get()} info!")
            driver.quit()
            input()
            sys.exit()

    def screen(self):
        database = pd.read_csv(os.getcwd() + '\\data\\database.csv') 
        tickers = []
        for row in database.to_numpy():
            tickers.append(row[0].split(" ")[0])
        tickers = sorted(list(set(tickers)))
        #Go through full ASX listing and extract name and sector of those listings which have data in database
        listings = {}
        for name, ticker, sector in pd.read_csv(os.getcwd() + '\\data\\ASXListedCompanies.csv', usecols=[0, 1, 2], header=None).values:
            if ticker in tickers:
                listings[ticker] = name, sector
        print("ticker list unfiltered: ", len(tickers), len(listings.keys()))

        criterion = {}
        criterion["Market cap"] = self.marketCapCriteria.getBounds()
        criterion["Dividends (¢)"] = self.dividendsCriteria.getBounds()
        criterion["Dividend Yield (%)"] = self.dividendYieldCriteria.getBounds()
        criterion["Book value ($)"] = self.bookValueCriteria.getBounds()
        criterion["Average annual P/E ratio (%)"] = self.priceEarningsCriteria.getBounds()
        criterion["Shares outstanding"] = self.sharesOutstandingCriteria.getBounds()
        criterion["Cash on hand"] = self.cashCriteria.getBounds()
        criterion["Net profit margin (%)"] = self.profitMarginCriteria.getBounds()
        criterion["S/T debt"] = self.shortDebtCriteria.getBounds()
        criterion["EBITDA"] = self.ebitdaCriteria.getBounds()
        criterion["Return on capital (%)"] = self.returnCapitalCriteria.getBounds()
        criterion["L/T Debt"] = self.longDebtCriteria.getBounds()

        functionalCriterion = {}
        functionalCriterion["EV"] = self.evMultipleCriteria.getBounds()
        functionalCriterion["CY"] = self.cashYieldCriteria.getBounds()
        functionalCriterion["ND:EBITDA"] = self.netDebtEbitdaRatioCriteria.getBounds()

        screenedLists = [] #List that stores lists of tickers that match criteria for each property
        screenedTickers = [] #List of tickers that match all criteria (intersect of lists in screen_lists)

        #Run the screening, parameter is SEARCH TYPE (recent year or average all years)
        screenedTickers = screener().mainScreen(self.master, tickers, database, criterion, functionalCriterion, self.search.get(), screenedLists, screenedTickers)
        print(len(screenedTickers))

        #Screen for sector
        screenedTickers = screener().sectorScreen(screenedTickers, self.sector.get(), listings, screenedLists)
        print(screenedTickers)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
