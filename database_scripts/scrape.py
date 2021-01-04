import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import bcrypt
import config
import time
import os
from bs4 import BeautifulSoup
import stdiomask
from tqdm import tqdm

def initial_login(password, tickers):
    try:
        driver.get(f"https://www.morningstar.com.au/Stocks/CompanyHistoricals/{tickers[0]}")
        WebDriverWait(driver, 30).until(lambda d: d.find_element_by_id('loginButton'))
        driver.find_element_by_id('loginButton').click()
        WebDriverWait(driver, 30).until(lambda d: d.find_element_by_id('loginFormNew'))
        driver.find_element_by_xpath("//input[contains(@type, 'email')]").send_keys(config.ms_username)
        driver.find_element_by_xpath("//input[contains(@type, 'password')]").send_keys(password)
        time.sleep(5)
        driver.find_element_by_xpath("//input[contains(@id, 'LoginSubmit')]").click()
        time.sleep(5)
        print("Morningstar login successful!") 
    except Exception as e: 
        print(e) 
        driver.quit()
        quit()

def data_scrape_page_one(ticker):
    driver.get(f"https://www.morningstar.com.au/Stocks/CompanyHistoricals/{ticker}")
    WebDriverWait(driver, 5).until(lambda d: d.find_element_by_id('pershare'))
    most_recent_year = driver.find_elements_by_xpath("//table[contains(@id, 'pershare')]/tbody/tr[1]/td")[-1].text.split("/")[1]
    html = driver.page_source
    soup = BeautifulSoup(html, features="html5lib")
    per_share_recent_year = pd.read_html(str(soup.findAll('table')[0]), header=None, skiprows=1)[0].iloc[:, [0, -1]]
    historical_financials_recent_year = pd.read_html(str(soup.findAll('table')[1]), header=None, skiprows=1)[0].iloc[:, [0, -1]]
    cash_flows_recent_year = pd.read_html(str(soup.findAll('table')[2]), header=None, skiprows=1)[0].iloc[:, [0, -1]]
    return ([
        most_recent_year,
        per_share_recent_year,
        historical_financials_recent_year,
        cash_flows_recent_year
    ])
    

def data_scrape_page_two(ticker):
    driver.get(f"https://www.morningstar.com.au/Stocks/BalanceSheet/{ticker}")
    WebDriverWait(driver, 5).until(lambda d: d.find_elements_by_id('comphist'))
    html = driver.page_source
    soup = BeautifulSoup(html, features="html5lib")
    debt_recent_year = pd.read_html(str(soup.findAll('table')[4]), header=None, skiprows=1)[0].iloc[:, [0, -1]]
    cash_recent_year = pd.read_html(str(soup.findAll('table')[2]), header=None, skiprows=1)[0].iloc[:, [0, -1]]
    return ([
        debt_recent_year, 
        cash_recent_year
    ])   

def get_recent_year_data(tickers):
    page_one_failed_tickers = []
    page_two_failed_tickers = []
    for ticker in tqdm(tickers):
        try:
            most_recent_year, per_share_recent_year, historical_financials_recent_year, cash_flows_recent_year = data_scrape_page_one(ticker)
        except:
            page_one_failed_tickers.append(ticker)
        try:
            debt_recent_year, cash_recent_year = data_scrape_page_two(ticker)
        except:
            page_two_failed_tickers.append(ticker)
        #concat to single df
        recent_data = pd.concat([
            per_share_recent_year,
            historical_financials_recent_year,
            cash_flows_recent_year,
            debt_recent_year,
            cash_recent_year
        ])
        #Updating existing DB with most recent year info
        update_db(ticker, most_recent_year, recent_data)
        
    database.to_csv(f'{directory}/database.csv', header=True, index=False)
    print(f"failed loading page one for the following tickers: {page_one_failed_tickers}")
    print(f"failed loading page two for the following tickers: {page_two_failed_tickers}")

def update_db(ticker, year, recent_data):
    column_to_update = '20' + year
    ticker_entries = database[database['Unnamed: 0'].str.contains(ticker)].iloc[:, 0]
    for entry in ticker_entries.items():
        for data in recent_data.to_numpy():
            if entry[1] == ticker + " " + data[0]:
                database.loc[entry[0], [column_to_update]] = data[1]
    
if __name__ == '__main__':
    #Set directory
    directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data'))
    if not os.path.exists(directory):
        os.makedirs(directory)

    #database location
    database = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data', 'database.csv')))

    #password
    ms_password = stdiomask.getpass(prompt="Enter morningstar password: \n")
    while not bcrypt.checkpw(ms_password.encode('utf8'), config.ms_password):
        print("Invalid Password. Please try again")
        ms_password = stdiomask.getpass(prompt="Enter morningstar password: \n")

    # ticker list
    # ticker_list = []
    # for value in pd.read_csv(f'{directory}/ASXListedCompanies.csv', usecols=[1], header=None).values:
    #     ticker_list.append(value[0])

    ticker_list = ['WPL', 'CBA', 'STO', 'DEG', 'SOL']

    #driver
    options = Options()
    options.headless = True
    geckodriver = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\web_driver', 'geckodriver.exe'))
    driver = webdriver.Firefox(executable_path=geckodriver, options=options)
    extensionDirectory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\web_driver\\extensions'))
    extensions = [
        '\\https-everywhere@eff.org.xpi',
        '\\uBlock0@raymondhill.net.xpi',
        '\\{e58d3966-3d76-4cd9-8552-1582fbc800c1}.xpi'
    ]
    for extension in extensions:
        driver.install_addon(extensionDirectory + extension, temporary=True)

    #run functions
    initial_login(ms_password, ticker_list)
    get_recent_year_data(ticker_list)

    # Stop Driver
    driver.quit()
