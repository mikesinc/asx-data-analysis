import numpy as np
import pandas as pd
import os

class Details:
    def __init__(self, ticker):
        self.ticker = ticker

    def listOperation(self, operation, list1, list2):
        if operation == "sum":
            return [round(a + b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "mul":
            return [round(a * b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "sub":
            return [round(a - b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]
        if operation == "div":
            return [round(a / b, 2) if isinstance(a, float) and isinstance(b, float) else "—" for a, b in zip(list1, list2)]

    def convertDictToList(self, dictionary):
        detailList = []
        for key, value in dictionary.items():
            temp = [key] + list(value)
            detailList.append(temp)
        return detailList

    def getDetails(self):
        #Get History
        # database = pd.read_csv(os.getcwd() + '\\data\\database.csv') 
        database = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..\\..\\data', 'database.csv')))
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
            if self.ticker in row[0]:
                for keyword in keywords:
                    if self.ticker + " " + keyword == row[0]:
                        valueList = []
                        for value in list(row)[1:]:
                            if value != "—":
                                value = float(value)
                            valueList.append(value)
                        detailDict[keyword] = np.array(valueList)
        return detailDict

    def getKeyDetails(self):
        detailList = self.convertDictToList(self.getDetails())
        keyDetailDict = {}
        kpiList = ['EBITDA (m)', 'L/T Debt', 'Market cap (m)', 'Cash', 'Dividends (¢)', 'Shares outstanding (m)', 'S/T debt']
        #check for KPI treeview
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
            cashYields = [round(ele * 100, 2) if isinstance(ele, float) else "—" for ele in list(self.listOperation("div", keyDetailDict['EBITDA (m)'], self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap (m)'])))]
            keyDetailDict['Cash Yield'] = cashYields

        if all(item in keyDetailDict for item in evMultipleList):
            evMultiples = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap (m)']), keyDetailDict['Cash']), keyDetailDict['EBITDA (m)'])
            keyDetailDict['EV Multiple'] = evMultiples

        if all(item in keyDetailDict for item in dividendsPaidList):
            keyDetailDict['Dividends paid ($M)'] = [round(ele / 100, 2) if isinstance(ele, float) else "—" for ele in list(self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding (m)']))]

        if all(item in keyDetailDict for item in percentEbitdaList):
            keyDetailDict['% EBDITA'] = self.listOperation("div", self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding (m)']), keyDetailDict['EBITDA (m)'])

        if all(item in keyDetailDict for item in netDebtRatioList):
            keyDetailDict['Net Debt : EBITDA'] = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['S/T debt']), keyDetailDict['Cash']), keyDetailDict['EBITDA (m)'])

        return keyDetailDict
