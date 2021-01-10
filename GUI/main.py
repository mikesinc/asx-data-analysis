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
from Components.Criteriawidget import *
from Components.Tvwidget import *
from Components.Calcinput import *
from Components.Calcoutput import *
from Components.Statoutput import *
from Components.Popup import *
from Functions.Screen import *
from Functions.Details import *
from tkinter import messagebox

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
        ttk.Button(self.inputFrame, text='Show Data for listing', width=20, command=self.printDetails).grid(row=2, column=0)
        ttk.Button(self.inputFrame, text='Refresh Daily Data', width=20, command=self.getDailyDetails).grid(row=3, column=0)
        ttk.Button(self.inputFrame, text='Quit', width=10, command=self.master.destroy).place(relx=0.9)
        ttk.Button(self.inputFrame, text='Update Database', width=18, command=self.confirm).place(relx=0.9, rely=0.03)

        # Frame for Treeview (info)
        self.infoFrame = ttk.LabelFrame(self.tabBook, text="Stock Summary")
        self.infoFrame.place(height=370, width=640, rely=0.12)
        #Treeview widget
        self.infoTv = Tvwidget(frame=self.infoFrame, columns=("Item", "Value"), relheight=1, relwidth=1)

        #Frame for Estimates (calculations)
        self.estimateFrame = ttk.LabelFrame(self.tabBook, text="Estimated forward values")
        self.estimateFrame.place(height=370, width=640, rely=0.12, relx=0.5)
        #Calc button
        ttk.Button(self.estimateFrame, text='Calculate Estimates', width=20, command=self.runEstimate).grid(row=0, column=2)
        #Entry fields
        self.ebitdaEntry = Calcinput(self.estimateFrame, text="EBITDA ($M)", row=0, col=0)
        self.sharesOutstandingEntry = Calcinput(self.estimateFrame, text="Shares Outstanding (M)", row=1, col=0)
        self.longDebtEntry = Calcinput(self.estimateFrame, text="L/T Debt ($M)", row=2, col=0)
        self.cashEntry = Calcinput(self.estimateFrame, text="Cash on hand ($M)", row=3, col=0)
        self.percentEbitdaEntry = Calcinput(self.estimateFrame, text="% EBITDA", row=4, col=0)
        tk.Label(self.estimateFrame, width=20).grid(row=5, column=0)

        #Calculated values
        self.medianPriceCalc = Calcoutput(self.estimateFrame, text="Median Price", row=6, col=0, width=20)
        self.averagePriceCalc = Calcoutput(self.estimateFrame, text="Average Price", row=7, col=0, width=20)
        self.minPriceCalc = Calcoutput(self.estimateFrame, text="Min Price", row=8, col=0, width=20)
        self.maxPriceCalc = Calcoutput(self.estimateFrame, text="Max Price", row=9, col=0, width=20)
        self.divPaidCalc = Calcoutput(self.estimateFrame, text="Dividends Paid ($M)", row=10, col=0, width=20)
        self.medianYieldCalc = Calcoutput(self.estimateFrame, text="Median Yield", row=11, col=0, width=20)
        self.averageYieldCalc = Calcoutput(self.estimateFrame, text="Average Yield", row=12, col=0, width=20)
        self.minYieldCalc = Calcoutput(self.estimateFrame, text="Minimum Yield", row=13, col=0, width=20)
        self.maxYieldCalc = Calcoutput(self.estimateFrame, text="Maximum Yield", row=14, col=0, width=20)
        self.assessedDivCalc = Calcoutput(self.estimateFrame, text="Assessed Dividend", row=15, col=0, width=20)

        #stats values
        tk.Label(self.estimateFrame, width=10, text="Cash Yield %").grid(row=5, column=3)
        tk.Label(self.estimateFrame, width=10, text="EV Multiple").grid(row=5, column=4)
        self.medianValueCalc = Statoutput(self.estimateFrame, text="Median Value", row=6, col=2, width=10)
        self.meanValueCalc = Statoutput(self.estimateFrame, text="Mean Value", row=7, col=2, width=10)
        self.stdValueCalc = Statoutput(self.estimateFrame, text="Std. Dev.", row=8, col=2, width=10)
        self.minValueCalc = Statoutput(self.estimateFrame, text="Min. value", row=9, col=2, width=10)
        self.maxValueCalc = Statoutput(self.estimateFrame, text="Max. value", row=10, col=2, width=10)

        #Frame for KPIs (Selected info from database)
        self.keyPerformanceFrame = ttk.LabelFrame(self.tabBook, text="Key Performance Indicators")
        self.keyPerformanceFrame.place(height=165, width=1280, rely=0.5)
        #Treeview widget
        self.keyPerformanceTv = Tvwidget(frame=self.keyPerformanceFrame, columns=tvcolumns, relheight=1, relwidth=1, firstColWidth=250, colWidth=100)

        #Frame for Details (Extended info from database)
        self.detailsFrame = ttk.LabelFrame(self.tabBook, text="Historical Performance")
        self.detailsFrame.place(height=300, width=1280, rely=0.67)
        #Treeview widget
        self.detailTv = Tvwidget(frame=self.detailsFrame, columns=tvcolumns, relheight=1, relwidth=1, firstColWidth=250, colWidth=100)

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
        self.search.set(1)
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
        self.optionmenu = ttk.OptionMenu(self.screenFrame, self.sector, *self.sectors)
        self.optionmenu.grid(row=14, column=6)
        self.optionmenu.config(width=20)

        #Entry fields for screening tool 
        self.marketCapCriteria = Criteriawidget(self.screenFrame, "Market Capital ($M)", 0, 0)
        self.sharesOutstandingCriteria = Criteriawidget(self.screenFrame, "Shares Outstanding (mil)", 4, 0)
        self.shortDebtCriteria = Criteriawidget(self.screenFrame, "Short-term debt ($M)", 8, 0)
        self.dividendsCriteria = Criteriawidget(self.screenFrame, "Dividends (¢)", 0, 3)
        self.dividendYieldCriteria = Criteriawidget(self.screenFrame, "Dividend yield (%)", 4, 3)
        self.ebitdaCriteria = Criteriawidget(self.screenFrame, "EBITDA ($M)", 8, 3)
        self.cashYieldCriteria = Criteriawidget(self.screenFrame, "Cash yield (%)", 0, 6)
        self.cashCriteria = Criteriawidget(self.screenFrame, "Cash on hand ($M)", 4, 6)
        self.longDebtCriteria = Criteriawidget(self.screenFrame, "Long-term debt ($M)", 8, 6)
        self.bookValueCriteria = Criteriawidget(self.screenFrame, "Book value ($)", 0, 9)
        self.evMultipleCriteria = Criteriawidget(self.screenFrame, "EV Multiple", 4, 9)
        self.returnCapitalCriteria = Criteriawidget(self.screenFrame, "Return on capital (%)", 8, 9)
        self.priceEarningsCriteria = Criteriawidget(self.screenFrame, "Price/Earnings (%)", 0, 12)
        self.profitMarginCriteria = Criteriawidget(self.screenFrame, "Profit Margin(%)", 4, 12)
        self.netDebtEbitdaRatioCriteria = Criteriawidget(self.screenFrame, "Net debt : EBITDA (ratio)", 8, 12)

        #Screening tool output frame
        self.screenOutput = ttk.LabelFrame(self.screenFrame, text="Search Results")
        self.screenOutput.place(height=650, width=1280, rely=0.29)

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
            "Return on capital (%)", 
            "Long-term debt ($M)"
            )
        self.screenTv = Tvwidget(self.screenOutput, 1, 1, columns, 250, 150)

    def confirm(self):
        Popup(self.master)
        
    def runEstimate(self):
        if self.tickerEntry.get() != "":
            if all(x != "" for x in [self.ebitdaEntry.getEntry(), self.longDebtEntry.getEntry(), self.cashEntry.getEntry(), self.sharesOutstandingEntry.getEntry(), self.percentEbitdaEntry.getEntry()]):
                self.medianPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.medianValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry(), 2)/self.sharesOutstandingEntry.getEntry())
                self.averagePriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.meanValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry(), 2)/self.sharesOutstandingEntry.getEntry())
                self.minPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.minValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry(), 2)/self.sharesOutstandingEntry.getEntry())
                self.maxPriceCalc.changeText(text=np.round(self.ebitdaEntry.getEntry()*self.maxValueCalc.getEvValue()-self.longDebtEntry.getEntry()+self.cashEntry.getEntry(), 2)/self.sharesOutstandingEntry.getEntry())
                self.divPaidCalc.changeText(text=self.ebitdaEntry.getEntry()*self.percentEbitdaEntry.getEntry()/100)

                self.assessedDivCalc.changeText(text=100*self.divPaidCalc.getValue()/self.sharesOutstandingEntry.getEntry())
                self.medianYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.medianPriceCalc.getValue(), 2)} %")
                self.averageYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.averagePriceCalc.getValue(), 2)} %")
                self.minYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.minPriceCalc.getValue(), 2)} %")
                self.maxYieldCalc.changeText(text=f"{np.round(self.assessedDivCalc.getValue()/self.maxPriceCalc.getValue(), 2)} %")
            else:
                messagebox.showinfo("Error", "Enter Estimates first...")
        else:
            messagebox.showinfo("Error", "Enter a ticker first...")

    def plotTrends(self):
        if self.tickerEntry.get() != "":
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
        else:
            messagebox.showinfo("Error", "Enter a ticker first...")
    
    def statCalc(self, statistic, list):
        try:
            if statistic == "median":
                return np.round(statistics.median(list), 1)
            elif statistic == "mean":
                return np.round(statistics.mean(list), 1)
            elif statistic == "stdev":
                return np.round(statistics.stdev(list), 1)
            elif statistic == "min":
                return np.round(statistics.stdev(list) - statistics.mean(list), 1)
            elif statistic == "max":
                return np.round(statistics.stdev(list) + statistics.mean(list), 1)
        except:
            return "—"

    def getStats(self):
        keyDetailDict = Details(self.tickerEntry.get()).getDetails(database,
                [
                    'EBITDA (m)', 
                    'L/T Debt', 
                    'Market cap (m)', 
                    'Cash', 
                    'Dividends (¢)', 
                    'Shares outstanding (m)', 
                    'S/T debt', 
                    'EV Multiple', 
                    'Dividends paid ($M)', 
                    'Cash Yield', 
                    '% EBDITA', 
                    'Net Debt : EBITDA'
                ]
            )
        self.medianValueCalc.changeCashYield(text=self.statCalc("median", [ele for ele in keyDetailDict['Cash Yield'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.meanValueCalc.changeCashYield(text=self.statCalc("mean", [ele for ele in keyDetailDict['Cash Yield'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.stdValueCalc.changeCashYield(text=self.statCalc("stdev", [ele for ele in keyDetailDict['Cash Yield'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.minValueCalc.changeCashYield(text=self.statCalc("min", [ele for ele in keyDetailDict['Cash Yield'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.maxValueCalc.changeCashYield(text=self.statCalc("max", [ele for ele in keyDetailDict['Cash Yield'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.medianValueCalc.changeEvValue(text=self.statCalc("median", [ele for ele in keyDetailDict['EV Multiple'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.meanValueCalc.changeEvValue(text=self.statCalc("mean", [ele for ele in keyDetailDict['EV Multiple'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.stdValueCalc.changeEvValue(text=self.statCalc("stdev", [ele for ele in keyDetailDict['EV Multiple'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.minValueCalc.changeEvValue(text=self.statCalc("min", [ele for ele in keyDetailDict['EV Multiple'] if isinstance(ele, float) and str(ele) != "nan"]))
        self.maxValueCalc.changeEvValue(text=self.statCalc("max", [ele for ele in keyDetailDict['EV Multiple'] if isinstance(ele, float) and str(ele) != "nan"]))
    
    def convertDictToList(self, dictionary):
        detailList = []
        for key, value in dictionary.items():
            temp = [key] + list(value)
            detailList.append(temp)
        return detailList
    
    def printDetails(self):
        if self.tickerEntry.get() != "":
            detailList = self.convertDictToList(Details(self.tickerEntry.get()).getDetails(database,
                [
                    'EBITDA (m)',
                    'EBIT (m)',
                    'L/T Debt',
                    'S/T debt',
                    'Market cap (m)',
                    'Dividends (¢)',
                    'Dividend yield (%)',
                    'Revenues (m)',
                    'Net profit (m)',
                    'Net profit margin(%)',
                    'Capital spending (¢)',
                    'Cash',
                    'Net operating cashflows (m)',
                    'Net investing cashflows (m)',
                    'Net financing cashflows (m)',
                    'Cash flow (¢)',
                    'Earnings pre abs (¢)',
                    'Book value ($)',
                    'Average annual P/E ratio (%)',
                    'Relative P/E (%)',
                    'Total return (%)',
                    'Depreciation (m)',
                    'Amortisation (m)',
                    'Income tax rate (%)',
                    'Employees (thousands)',
                    'Shareholders equity',
                    'Return on capital (%)',
                    'Return on equity (%)',
                    'Payout ratio (%)',
                    'Shares outstanding (m)'
                ]
            ))
            self.detailTv.clear()
            for count, row in enumerate(detailList):
                self.detailTv.insertValues([value if str(value) != "nan" else "—" for value in row], count)

            keyDetailList = self.convertDictToList(Details(self.tickerEntry.get()).getDetails(database,
                [
                    'EBITDA (m)', 
                    'L/T Debt', 
                    'Market cap (m)', 
                    'Cash', 
                    'Dividends (¢)', 
                    'Shares outstanding (m)', 
                    'S/T debt', 
                    'EV Multiple', 
                    'Dividends paid ($M)', 
                    'Cash Yield', 
                    '% EBDITA', 
                    'Net Debt : EBITDA'
                ]
            ))
            self.keyPerformanceTv.clear()
            for count, row in enumerate(keyDetailList):
                self.keyPerformanceTv.insertValues([value if str(value) != "nan" else "—" for value in row], count)
            
            self.getStats()
        else:
            messagebox.showinfo("Error", "Enter a ticker first...")

    def getDailyDetails(self):
        if self.tickerEntry.get() != "":
            # initialise driver
            print("....LOADING: Starting Web Driver...")
            options = Options()
            options.headless = True
            # geckodriver = os.getcwd() + '\\web_driver\\geckodriver.exe'
            # Geckodriver library modified to ensures NO CMD window is opened with geckodriver
            geckodriver = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\web_driver', 'geckodriver.exe'))
            driver = webdriver.Firefox(executable_path=geckodriver, options=options)
            # extensionDirectory = os.getcwd() + '\\web_driver\\extensions\\driver_extensions\\'
            extensionDirectory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\web_driver\\extensions'))
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
                self.infoTv.clear()
                for i, item in enumerate(detailDictionary):
                    self.infoTv.insertValues((item, detailDictionary[item]), i)
                #stop driver
                driver.quit()
            except:
                print(f"Something went wrong scraping {self.tickerEntry.get()} info!")
                driver.quit()
                input()
                sys.exit()
        else:
            messagebox.showinfo("Error", "Enter a ticker first...")

    def screen(self):
        criterion = {}
        criterion["EV Multiple"] = self.evMultipleCriteria.getBounds()
        criterion["Cash Yield"] = self.cashYieldCriteria.getBounds()
        criterion["Net Debt : EBITDA"] = self.netDebtEbitdaRatioCriteria.getBounds()
        criterion["Market cap (m)"] = self.marketCapCriteria.getBounds()
        criterion["Dividends (¢)"] = self.dividendsCriteria.getBounds()
        criterion["Dividend Yield (%)"] = self.dividendYieldCriteria.getBounds()
        criterion["Book value ($)"] = self.bookValueCriteria.getBounds()
        criterion["Average annual P/E ratio (%)"] = self.priceEarningsCriteria.getBounds()
        criterion["Shares outstanding (m)"] = self.sharesOutstandingCriteria.getBounds()
        criterion["Cash"] = self.cashCriteria.getBounds()
        criterion["Net profit margin (%)"] = self.profitMarginCriteria.getBounds()
        criterion["S/T debt"] = self.shortDebtCriteria.getBounds()
        criterion["EBITDA (m)"] = self.ebitdaCriteria.getBounds()
        criterion["Return on capital (%)"] = self.returnCapitalCriteria.getBounds()
        criterion["L/T Debt"] = self.longDebtCriteria.getBounds()

        # functionalCriterion = {}
        screenResults = Screen(database, ASXtickerlist, criterion, self.search.get(), self.sector.get()).screen()

        self.screenTv.clear()
        for count, row in enumerate(screenResults):
            self.screenTv.insertValues([value if str(value) != "nan" else "—" for value in row], count)

if __name__ == "__main__":
    database = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data', 'database.csv')))
    ASXtickerlist = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data', 'ASXListedCompanies.csv'))
    tvcolumns = ['Property'] + [x for x in database.columns[1:]]
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
