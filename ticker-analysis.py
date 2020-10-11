#Import libraries
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter.ttk import *

#Get historical data
def get_stock_history():
    sheet_dict = {'historical price - max': '1d', 'historical price - 5y': '1d', 'historical price - 1y': '1d', 'historical price - 6mo': '1d', 'historical price - 3mo': '1d', 'historical price - 1mo': '1d', 'historical price - 5d': '60m', 'historical price - 1d': '1m'}    
    try:      
        #Plot trend data for all time periods
        plotpos = 1
        for sheet in sheet_dict.keys():   
            sheet_dict[sheet] = yf.download(ticker_entry.get()+'.AX', period=sheet.split("- ")[1], interval=sheet_dict[sheet])   
            trends.add_subplot(4, 2, plotpos, title=f"{ticker_entry.get()} - {sheet}", ylabel="$AUD").plot(sheet_dict[sheet]['Close']) 
            plotpos += 1
        #Add to tinker GUI
        chart = FigureCanvasTkAgg(trends, trends_frame)
        chart.get_tk_widget().place(relheight=1, relwidth=1)   
    except:
        print(f"Something went wrong retrieving {ticker_entry.get()} historical data")
        print('Press enter to close...')
        input()
        sys.exit()

def get_info():
    # initialise driver
    print("....LOADING: Starting Web Driver...")
    options = Options()
    options.headless = True
    geckodriver = os.getcwd() + '\\geckodriver.exe'
    # geckodriver = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'geckodriver.exe'))
    driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    extension_dir = os.getcwd() + '\\driver_extensions\\'
    # extension_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'driver_extensions'))
    extensions = [
        '\\https-everywhere@eff.org.xpi',
        '\\uBlock0@raymondhill.net.xpi',
    ]
    for extension in extensions:
        driver.install_addon(extension_dir + extension, temporary=True)
    
    #Get ticker info
    try:
        driver.get(f"https://www.morningstar.com.au/Stocks/NewsAndQuotes/{ticker_entry.get()}")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
    except:
        print(f"Something went wrong loading the {ticker_entry.get()} morning star page!")
        driver.quit()
        print('Press enter to close...')
        input()
        sys.exit()
    try:
        html = driver.page_source
        soup = BeautifulSoup(html,'html.parser')
        info_set = {}
        info_set['Name'] = driver.find_element_by_xpath("//h1[contains(@class, 'N_QHeader_b')]/label").text
        info_set['Value'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[1]/span/span[2]").text
        info_set['Day change cents'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[2]/div[2]/span[1]").text
        info_set['Day change percent'] = driver.find_element_by_xpath("//div[contains(@class, 'N_QPriceLeft')]/div[2]/div[2]/span[3]").text
        as_of_text = Label(input_frame, text=driver.find_element_by_class_name("N_QText").text) 
        as_of_text.grid(row=2, column=2)
        for item in soup.findAll('td'):
            if item.find('span') and item.find('h3'):
                info_set[item.find('h3').text] = item.find('span').text
        if info_set['\xa0Company Profile']:
            del info_set['\xa0Company Profile']
        if info_set['Equity Style Box']:
            del info_set['Equity Style Box']
        info_set['Market Cap'].replace("\xa0", "").replace(",", "").replace("M", "000000").replace("B", "000000000")
        #Populate Tkinter treeview
        count = 0
        for item in info_set:
            info_tv.insert(parent="", index="end", iid=count, text="", values=(item, info_set[item]))
            count += 1

        #stop driver
        driver.quit()
    except:
        print(f"Something went wrong scraping {ticker_entry.get()} info!")
        driver.quit()
        print('Press enter to close...')
        input()
        sys.exit()

if __name__ == '__main__':
    #Master GUI
    master = Tk()
    master.geometry("1280x960")
    master.pack_propagate(False)
    master.resizable(0, 0)
    master.title('ASX Stock Analysis')

    #Frame for input
    input_frame = LabelFrame(master, text="User Input")
    input_frame.place(height=100, width=1280)
    #Lables
    ASX_Label = Label(input_frame, text="ASX ticker")
    ASX_Label.grid(row=0, column=1)
    ticker_entry = Entry(input_frame, width=20)
    ticker_entry.grid(row=0, column=0)
    #Buttons
    myButton = Button(input_frame, text='Show stock trend data', width=20, command=get_stock_history)
    myButton.grid(row=1, column=0)
    myButton = Button(input_frame, text='Get stock info', width=20, command=get_info)
    myButton.grid(row=2, column=0)

    #Frame for Treeview (info)
    info_frame = LabelFrame(master, text="Stock Info")
    info_frame.place(height=440, width=1280, rely=0.1)
    #Treeview widget
    info_tv = Treeview(info_frame)
    info_tv.place(relheight=1, relwidth=1)
    treescrolly = Scrollbar(info_frame, orient="vertical", command=info_tv.yview)
    treescrollx = Scrollbar(info_frame, orient="horizontal", command=info_tv.xview)
    info_tv.configure(xscrollcommand=treescrollx.set, yscrollcomman=treescrolly.set)
    treescrollx.pack(side="bottom", fill="x")
    treescrolly.pack(side="right", fill="y")
    #Define and format columns
    info_tv["columns"] = ("Item", "Value")
    info_tv.column("#0", width=0, stretch=NO)
    info_tv.column("Item")
    info_tv.column("Value")
    #Create headings
    info_tv.heading("#0", text="")
    info_tv.heading("Item", text="Item", anchor=W)
    info_tv.heading("Value", text="Value", anchor=W)

    #Frame for Trend Plots
    trends_frame = LabelFrame(master, text="Trend Plots")
    trends_frame.place(height=420, width=1280, rely=0.56)
    trends = plt.figure()

    master.mainloop()