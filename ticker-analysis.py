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
import tkinter as tk
from tkinter import *

#Get historical data
def get_stock_history(ticker):
    sheet_dict = {'historical price - max': '1d', 'historical price - 5y': '1d', 'historical price - 1y': '1d', 'historical price - 6mo': '1d', 'historical price - 3mo': '1d', 'historical price - 1mo': '1d', 'historical price - 5d': '60m', 'historical price - 1d': '1m'}    
    try:      
        #Plot trend data for all time periods
        plt.figure()
        plotpos = 1
        for sheet in sheet_dict.keys():   
            plt.subplot(4, 2, plotpos)
            plt.title(f"{ticker} - {sheet}")
            plt.ylabel("$AUD")
            sheet_dict[sheet] = yf.download(ticker+'.AX', period=sheet.split("- ")[1], interval=sheet_dict[sheet])   
            plt.plot(sheet_dict[sheet]['Close']) 
            plotpos += 1
        plt.show()
    except:
        print(f"Something went wrong retrieving {ticker} historical data")
        print('Press enter to close...')
        input()
        sys.exit()

#Get financials
def get_info(ticker):
    try:
        driver.get(f"https://www.morningstar.com.au/Stocks/NewsAndQuotes/{ticker}")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
    except:
        print(f"Something went wrong loading the {ticker} morning star page!")
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
        info_set['As of text'] = driver.find_element_by_class_name("N_QText").text
        for item in soup.findAll('td'):
            if item.find('span') and item.find('h3'):
                info_set[item.find('h3').text] = item.find('span').text   
        info_set['Market Cap'].replace("\xa0", "").replace(",", "").replace("M", "000000").replace("B", "000000000")

        ticker_info = pd.DataFrame.from_dict(info_set, orient='index')
    except:
        print(f"Something went wrong scraping {ticker} info!")
        driver.quit()
        print('Press enter to close...')
        input()
        sys.exit()

#Construct GUI
def start(): 
    master = Tk()
    master.title('ASX Stock Analysis')
    historical_data = Canvas(master, width=800, height=640)
    Label(master, text="ASX ticker").grid(row=0)
    ticker = Entry(master)
    ticker.grid(row=0, column=1)  
    Button(master, text='Run Analysis', width=20, command=master.destroy).grid(row=0, column=2)
    mainloop()

if __name__ == '__main__':
    start()
    # ticker = input('Please enter ASX ticker: ')
    # # initialise driver
    # print("....LOADING: Starting Web Driver...")
    # options = Options()
    # options.headless = True
    # geckodriver = os.getcwd() + '\\geckodriver.exe'
    # # geckodriver = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'geckodriver.exe'))
    # driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    # extension_dir = os.getcwd() + '\\driver_extensions\\'
    # # extension_dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'driver_extensions'))
    # extensions = [
    #     '\\https-everywhere@eff.org.xpi',
    #     '\\uBlock0@raymondhill.net.xpi',
    #     ]
    # for extension in extensions:
    #     driver.install_addon(extension_dir + extension, temporary=True)
    # # Scrape stock daily info
    # print("....LOADING: Retrieving stock info data")
    # get_info(ticker)
    # # stop driver
    # driver.quit()
    # print("....LOADING: Retrieving historical stock price trend data")
    # # get_stock_history(ticker)
    # print("....LOADING DONE!")