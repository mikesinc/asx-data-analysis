from GUI import *

class Screen:
    def __init__(self, database, criterion, functionalCriterion, searchType, sector):
        self.database = database
        self.criterion = criterion
        self.functionalCriterion = functionalCriterion
        self.searchType = searchType
        self.sector = sector

    def checkEntry(self, entry):
        try:
            if float(entry) or float(entry) == 0:
                return float(entry)
        except:
            return False

    def checkBounds(self, value, Max, Min, Dict, ticker):
        #Check if criteria entered
        if self.checkEntry(Max) or self.checkEntry(Min):
            #Check if has min AND max criteria
            if not value == "—":
                if self.checkEntry(Max) and self.checkEntry(Min):
                #Add tickers within criteria range
                    if float(value) >= self.checkEntry(Min) and float(value) <= self.checkEntry(Max):
                        Dict[ticker] = float(value)
                #Check if has max criteria
                elif self.checkEntry(Max):
                    #Add tickers that are below max criteria
                    if float(value) <= self.checkEntry(Max):
                        Dict[ticker] = float(value)
                #Check if has min criteria
                elif self.checkEntry(Min):
                    #Add tickers that are above min criteria
                    if float(value) >= self.checkEntry(Min):
                        Dict[ticker] = float(value)
        #If there are no bounds set, add the ticker
        else:
            Dict[ticker] = value

    def basicScreen(self, tickers):
        #Go through database and screen tickers
        tickerProps = {}
        for ticker in tickers:
            tickerProps[ticker] = []
        for row in self.database.to_numpy():
            ticker = row[0].split(" ")[0]
            if ticker in tickers:
                for Property in self.criterion.keys():
                    if Property in row[0] and not "from" in row[0] and not "available" in row[0]: #ensure "from" and "available" aren't in the word to remove extra net income results
                        tickerProps[ticker].append(Property) 
                        if self.searchType == 2: #if search type is average of all years since 2010 (search type == 2), get average value
                            values = []
                            for value in row[range(1, len(row))]:
                                if not value == "—":
                                    values.append(float(value))
                            if len(values):
                                value = mean(values)
                        else:
                            value = row[len(row)-1]
                        self.checkBounds(value, self.criterion[Property]['max'], self.criterion[Property]['min'], self.criterion[Property]['screened'], row[0].split(" ")[0])      
        
        #If the ticker did not have the property listed in the database, do a check anyway on a default "—" value, so that it is still added to the results
        #given there were no criteria entered for that specific property.
        for ticker in tickerProps:
            for Property in self.criterion.keys():
                if not Property in tickerProps[ticker]:
                    self.checkBounds("—", self.criterion[Property]['max'], self.criterion[Property]['min'], self.criterion[Property]['screened'], ticker)

    def functionalScreen(self, tickers):
        for ticker in tickers:
            keyDetailDict = Details(ticker).getKeyDetails()
            if self.searchType == 1:
                cashYield = keyDetailDict["Cash Yield"][9]
                evMultiple = keyDetailDict["EV Multiple"][9]
                netDebtEbitdaRatio = keyDetailDict["Net Debt : EBITDA"][9]
            else:
                try:
                    cashYield = sum([ele for ele in keyDetailDict["Cash Yield"] if isinstance(ele, float)])/len([ele for ele in keyDetailDict["Cash Yield"] if isinstance(ele, float)])
                except:
                    cashYield = "—"
                try: 
                    evMultiple = sum([ele for ele in keyDetailDict["EV Multiple"] if isinstance(ele, float)])/len([ele for ele in keyDetailDict["EV Multiple"] if isinstance(ele, float)])
                except:
                    evMultiple = "—"
                try:
                    netDebtEbitdaRatio = sum([ele for ele in keyDetailDict["Net Debt : EBITDA"] if isinstance(ele, float)])/len([ele for ele in keyDetailDict["Net Debt : EBITDA"] if isinstance(ele, float)])
                except:
                    netDebtEbitdaRatio = "—"

            #check against criteria
            self.checkBounds(cashYield, self.functionalCriterion['CY']['max'], self.functionalCriterion['CY']['min'], self.functionalCriterion['CY']['screened'], ticker)
            self.checkBounds(evMultiple, self.functionalCriterion['EV']['max'], self.functionalCriterion['EV']['min'], self.functionalCriterion['EV']['screened'], ticker)
            self.checkBounds(netDebtEbitdaRatio, self.functionalCriterion['ND:EBITDA']['max'], self.functionalCriterion['ND:EBITDA']['min'], self.functionalCriterion['ND:EBITDA']['screened'], ticker)

    def sectorScreen(self, tickers, listings):
        sectorFilteredTickers = [] #Redefine as empty list to be filled with tickers matching sector
        sectorCriteria = self.sector
        for ticker in tickers:
            if listings[ticker][1] == sectorCriteria:
                sectorFilteredTickers.append(ticker)
        return sectorFilteredTickers

    def screen(self):
        screenedTickers = []
        for row in self.database.to_numpy():
            screenedTickers.append(row[0].split(" ")[0])
        screenedTickers = sorted(list(set(screenedTickers)))
        #Go through full ASX listing and extract name and sector of those listings which have data in database
        listings = {}
        for name, ticker, sector in pd.read_csv(os.getcwd() + '\\data\\ASXListedCompanies.csv', usecols=[0, 1, 2], header=None).values:
            if ticker in screenedTickers:
                listings[ticker] = name, sector
        print("ticker list unfiltered: ", len(screenedTickers), len(listings.keys()))

        screenedLists = [] #List that stores lists of tickers that match criteria for each property

        #If sector criteria defined, further screen for this
        if not self.sector == "All":
            sectorFilteredTickers = self.sectorScreen(screenedTickers, listings)
            screenedLists.append(sectorFilteredTickers)
            screenedTickers = sorted(list(set(screenedLists[0]).intersection(*screenedLists)))
        print("ticker list after sector: ", len(screenedTickers)) 

        self.basicScreen(screenedTickers)
        for Property in self.criterion.keys():
            screenedLists.append(self.criterion[Property]['screened'])
        screenedTickers = sorted(list(set(screenedLists[0]).intersection(*screenedLists)))
        print("ticker list after basic: ", len(screenedTickers))

        self.functionalScreen(screenedTickers)
        for Property in self.functionalCriterion.keys():
            screenedLists.append(self.functionalCriterion[Property]['screened'])
        screenedTickers = sorted(list(set(screenedLists[0]).intersection(*screenedLists)))
        print("ticker list after functional: ", len(screenedTickers))

        rows = []
        for ticker in screenedTickers:
            row = [listings[ticker][0], ticker, listings[ticker][1]]
            for Property in self.functionalCriterion.keys():
                row.append(self.functionalCriterion[Property]['screened'][ticker])
            for Property in self.criterion.keys():
                row.append(self.criterion[Property]['screened'][ticker])
            rows.append(row)
        return rows
