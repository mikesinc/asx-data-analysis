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
import numpy as np

def convertDictToList(dictionary):
    detailList = []
    for key, value in dictionary.items():
        temp = [key] + list(value)
        detailList.append(temp)
    return detailList

def type_convert(ele):
    try:
        return float(ele)
    except:
        return ele

def listOperation(operation, list1, list2):
    if operation == "sum":
        return [round(type_convert(a) + type_convert(b), 2) if isinstance(type_convert(a), float) and isinstance(type_convert(b), float) else "—" for a, b in zip(list1, list2)]
    if operation == "mul":
        return [round(type_convert(a) * type_convert(b), 2) if isinstance(type_convert(a), float) and isinstance(type_convert(b), float) else "—" for a, b in zip(list1, list2)]
    if operation == "sub":
        return [round(type_convert(a) - type_convert(b), 2) if isinstance(type_convert(a), float) and isinstance(type_convert(b), float) else "—" for a, b in zip(list1, list2)]
    if operation == "div":
        return [round(type_convert(a) / type_convert(b), 2) if isinstance(type_convert(a), float) and isinstance(type_convert(b), float) and type_convert(b) != 0 else "—" for a, b in zip(list1, list2)]

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
        if 10 < int(most_recent_year) < 50:
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
                database.loc[entry[0], [column_to_update]] = "—" if data[1] == "--" else data[1]

def getDetails(ticker):
    keywords = ['EBITDA (m)',
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
                'Shares outstanding (m)']
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

def getKeyDetails(ticker):
    detailList = convertDictToList(getDetails(ticker))
    keyDetailDict = {}
    func_properties = {}
    kpiList = ['EBITDA (m)', 'L/T Debt', 'Market cap (m)', 'Cash', 'Dividends (¢)', 'Shares outstanding (m)', 'S/T debt']
    for row in detailList:
        if row[0] in kpiList:
            valueList = []
            for value in list(row)[1:]:
                if value != "—":
                    value = float(value)
                valueList.append(value)
            keyDetailDict[row[0]] = np.array(valueList)
    cashYieldList = ['EBITDA (m)', 'L/T Debt', 'Market cap (m)']
    evMultipleList = ['L/T Debt', 'Market cap (m)', 'Cash']
    dividendsPaidList = ['Dividends (¢)', 'Shares outstanding (m)']
    percentEbitdaList = ['Dividends (¢)', 'Shares outstanding (m)', 'EBITDA (m)']
    netDebtRatioList = ['L/T Debt', 'S/T debt', 'Cash', 'EBITDA (m)']
    
    if all(item in keyDetailDict for item in cashYieldList):
        cashYields = [round(ele * 100, 2) if isinstance(ele, float) else "—" for ele in list(listOperation("div", keyDetailDict['EBITDA (m)'], listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap (m)'])))]
        func_properties[f'{ticker} Cash Yield'] = cashYields

    if all(item in keyDetailDict for item in evMultipleList):
        evMultiples = listOperation("div", listOperation("sub", listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap (m)']), keyDetailDict['Cash']), keyDetailDict['EBITDA (m)'])
        func_properties[f'{ticker} EV Multiple'] = evMultiples

    if all(item in keyDetailDict for item in dividendsPaidList):
        func_properties[f'{ticker} Dividends paid ($M)'] = [round(ele / 100, 2) if isinstance(ele, float) else "—" for ele in list(listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding (m)']))]

    if all(item in keyDetailDict for item in percentEbitdaList):
        func_properties[f'{ticker} % EBDITA'] = listOperation("div", listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding (m)']), keyDetailDict['EBITDA (m)'])

    if all(item in keyDetailDict for item in netDebtRatioList):
        func_properties[f'{ticker} Net Debt : EBITDA'] = listOperation("div", listOperation("sub", listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['S/T debt']), keyDetailDict['Cash']), keyDetailDict['EBITDA (m)'])

    df = pd.DataFrame.from_dict(func_properties, orient="index").reset_index()
    df.columns = database.columns
    return df

def append_functional_properties(tickers):
    functional_property_df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data', 'database.csv')))
    failed_funcs = []
    for ticker in tqdm(tickers):
        try:
            functional_property_df = pd.concat([functional_property_df, getKeyDetails(ticker)])
        except:
            failed_funcs.append(ticker)
    functional_property_df.drop_duplicates(subset=['Unnamed: 0'], keep="last", inplace=True)
    functional_property_df.to_csv(f'{directory}/database.csv', header=True, index=False)
    print(f"failed functional calcs for the following tickers: {failed_funcs}")

if __name__ == '__main__':
    #Set directory
    directory = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data'))
    if not os.path.exists(directory):
        os.makedirs(directory)

    #database location
    database = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\data', 'database.csv')))

    # password
    ms_password = stdiomask.getpass(prompt="Enter morningstar password: \n")
    while not bcrypt.checkpw(ms_password.encode('utf8'), config.ms_password):
        print("Invalid Password. Please try again")
        ms_password = stdiomask.getpass(prompt="Enter morningstar password: \n")

    # ticker list
    ticker_list = []
    for value in pd.read_csv(f'{directory}/ASXListedCompanies.csv', usecols=[1], header=None).values:
        ticker_list.append(value[0])

    # ticker_list = ['WPL', 'CBA', 'STO', 'DEG', 'SOL']
    # ticker_list = ['HOT', 'LON']
    # ticker_list = ['VBS']

    driver
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

    run functions
    initial_login(ms_password, ticker_list)
    get_recent_year_data(ticker_list)
    append_functional_properties(ticker_list)

    # Stop Driver
    driver.quit()
