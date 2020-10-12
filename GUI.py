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
        self.stockButton = ttk.Button(self.inputFrame, text='Update Data', width=20, command=self.getDetails) #add command
        self.stockButton.grid(row=2, column=0)
        self.quitButton = ttk.Button(self.inputFrame, text='Quit', width=10, command=self.master.destroy) #add command
        self.quitButton.place(relx=0.9)

        # Frame for Treeview (info)
        self.infoFrame = ttk.LabelFrame(self.tabBook, text="Stock Summary")
        self.infoFrame.place(height=400, width=640, rely=0.12)
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
        self.estimateFrame.place(height=400, width=640, rely=0.12, relx=0.5)

        #Frame for Details (Extended info from database)
        self.detailsFrame = ttk.LabelFrame(self.tabBook, text="Historical Performance")
        self.detailsFrame.place(height=420, width=1280, rely=0.55)
        #Treeview widget
        self.detailTv = ttk.Treeview(self.detailsFrame)
        self.detailTv.place(relheight=1, relwidth=1)
        self.dtreescrolly = ttk.Scrollbar(self.detailsFrame, orient="vertical", command=self.detailTv.yview)
        self.dtreescrollx = ttk.Scrollbar(self.detailsFrame, orient="horizontal", command=self.detailTv.xview)
        self.detailTv.configure(xscrollcommand=self.dtreescrollx.set, yscrollcommand=self.dtreescrolly.set)
        self.dtreescrollx.pack(side="bottom", fill="x")
        self.dtreescrolly.pack(side="right", fill="y")
        #Define and format columns
        self.detailTv["columns"] = ("", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019")
        self.detailTv.column("#0", width=0, stretch=False)
        for column in self.detailTv["columns"]:
            self.detailTv.column(column, width=10)
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
            if detailDictionary['Equity Style Box']:
                del detailDictionary['Equity Style Box']
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

        #Get History
        try:
            database = pd.read_csv(os.getcwd() + '\\data\\database.csv', index_col=0) 
            countd = 0
            keywords = ['EDBITDA',
                    'EBIT',
                    'L/T debt',
                    'S/T debt',
                    'Market Cap ',
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
            for entry in database.iterrows():
                if self.tickerEntry.get() in entry[0] and entry[0].split(" ")[1] in keywords:
                    self.detailTv.insert(parent="", index="end", iid=countd, text="", values=[entry])
                    countd += 1
        except:
            print(f"Something went getting historical data for {self.tickerEntry.get()}!")
            input()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()