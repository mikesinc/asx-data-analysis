import numpy as np
import pandas as pd
import os

class Details:
    def __init__(self, ticker):
        self.ticker = ticker

    def getDetails(self, database, keywords):
        #Get History
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
