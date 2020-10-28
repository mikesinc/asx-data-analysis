from GUI import *

class screener:
    def checkBounds(self, value, Max, Min, Dict, ticker):
        try:
            Max = float(Max)
        except:
            Max = None
        try:
            Min = float(Min)
        except:
            Max = None
        #Check if criteria entered
        print(Max, Min)
        if Max != None or Min != None:
            #Check if has min AND max criteria
            if not value == "—":
                if (Max and Min) or (Max == 0 and Min) or (Max and Min == 0):
                #Add tickers within criteria range
                    if float(value) >= Min and float(value) <= Max:
                        Dict[ticker] = float(value)
                #Check if has max criteria
                elif Max:
                    #Add tickers that are below max criteria
                    if float(value) <= Max:
                        Dict[ticker] = float(value)
                #Check if has min criteria
                elif Min:
                    #Add tickers that are above min criteria
                    if float(value) >= Min:
                        Dict[ticker] = float(value)
        #If there are no bounds set, add the ticker
        else:
            Dict[ticker] = value

    def basicScreen(self, tickers, database, criterion, searchType):
        #Go through database and screen tickers
        tickerProps = {}
        for ticker in tickers:
            tickerProps[ticker] = []
        for row in database.to_numpy():
            ticker = row[0].split(" ")[0]
            for Property in criterion.keys():
                if Property in row[0] and not "from" in row[0] and not "available" in row[0]: #ensure "from" and "available" aren't in the word to remove extra net income results
                    tickerProps[ticker].append(Property) 
                    if searchType == 2: #if search type is average of all years since 2010 (search type == 2), get average value
                        values = []
                        for value in row[range(1, len(row))]:
                            if not value == "—":
                                values.append(float(value))
                        if len(values):
                            value = mean(values)
                    else:
                        value = row[len(row)-1]
                    self.checkBounds(value, criterion[Property]['max'], criterion[Property]['min'], criterion[Property]['screened'], row[0].split(" ")[0])      
        
        #If the ticker did not have the property listed in the database, do a check anyway on a default "—" value, so that it is still added to the results
        #given there were no criteria entered for that specific property.
        for ticker in tickerProps:
            for Property in criterion.keys():
                if not Property in tickerProps[ticker]:
                    self.checkBounds("—", criterion[Property]['max'], criterion[Property]['min'], criterion[Property]['screened'], ticker)

    def mainScreen(self, master, tickers, database, criterion, functionalCriterion, searchType, screenedLists, screenedTickers):
        #Collect formula inputs by running initial screening for the required inputs
        self.basicScreen(tickers, database, criterion, searchType)
        for Property in criterion.keys():
            screenedLists.append(criterion[Property]['screened'])
        screenedTickers = sorted(list(set(screenedLists[0]).intersection(*screenedLists)))

        marketCapValues = criterion['Market cap']['screened']
        longtermDebtValues = criterion['L/T Debt']['screened']
        shorttermDebtValues = criterion['S/T debt']['screened']
        totalCashValues = criterion['Cash on hand']['screened']
        ebitdaValues = criterion['EBITDA']['screened']

        for ticker in screenedTickers:
            keyDetailDict = MainApplication(master).getKeyDetails(ticker)
            cashYield = keyDetailDict["Cash Yield"]
            evMultiple = keyDetailDict["EV Multiple"]
            netDebtEbitdaRatio = keyDetailDict["Net Debt : EBITDA"]

            #check against criteria
            self.checkBounds(cashYield, functionalCriterion['CY']['max'], functionalCriterion['CY']['min'], functionalCriterion['CY']['screened'], ticker)
            self.checkBounds(evMultiple, functionalCriterion['EV']['max'], functionalCriterion['EV']['min'], functionalCriterion['EV']['screened'], ticker)
            self.checkBounds(netDebtEbitdaRatio, functionalCriterion['ND:EBITDA']['max'], functionalCriterion['ND:EBITDA']['min'], functionalCriterion['ND:EBITDA']['screened'], ticker)

        for Property in functionalCriterion.keys():
            screenedLists.append(functionalCriterion[Property]['screened'])
        return sorted(list(set(screenedLists[0]).intersection(*screenedLists)))

    def sectorScreen(self, screenedTickers, sector, listings, screenedLists):
        sectorFilteredTickers = screenedTickers #Default to list of all tickers after main screening
        if not sector == "All": #If sector criteria defined, further screen for this
            sectorFilteredTickers = [] #Redefine as empty list to be filled with tickers matching sector
            sectorCriteria = sector
            for ticker in screenedTickers:
                if listings[ticker][1] == sectorCriteria:
                    sectorFilteredTickers.append(ticker)
        screenedLists.append(sectorFilteredTickers)
        return sorted(list(set(screenedLists[0]).intersection(*screenedLists)))
