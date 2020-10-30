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
        else:
            keyDetailDict['Cash Yield'] = ["—"] * 10

        if all(item in keyDetailDict for item in evMultipleList):
            evMultiples = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['Market cap ']), keyDetailDict['Cash on hand']), keyDetailDict['EBITDA'])
            keyDetailDict['EV Multiple'] = evMultiples
        else:
            keyDetailDict['EV Multiple'] = ["—"] * 10

        if all(item in keyDetailDict for item in dividendsPaidList):
            keyDetailDict['Dividends paid ($M)'] = [round(ele / 100, 2) if isinstance(ele, float) else "—" for ele in list(self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding ']))]
        else:
            keyDetailDict['Dividends paid ($M)'] = ["—"] * 10

        if all(item in keyDetailDict for item in percentEbitdaList):
            keyDetailDict['% EBDITA'] = self.listOperation("div", self.listOperation("mul", keyDetailDict['Dividends (¢)'], keyDetailDict['Shares outstanding ']), keyDetailDict['EBITDA'])
        else:
            keyDetailDict['% EBDITA'] = ["—"] * 10

        if all(item in keyDetailDict for item in netDebtRatioList):
            keyDetailDict['Net Debt : EBITDA'] = self.listOperation("div", self.listOperation("sub", self.listOperation("sum", keyDetailDict['L/T Debt'], keyDetailDict['S/T debt']), keyDetailDict['Cash on hand']), keyDetailDict['EBITDA'])
        else:
            keyDetailDict['Net Debt : EBITDA'] = ["—"] * 10

        return keyDetailDict