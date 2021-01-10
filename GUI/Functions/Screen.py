# from GUI import *
from Functions.Details import *
import statistics

class Screen:
    def __init__(self, database, ASX_tickerlist, criterion, searchType, sector):
        self.database = database
        self.criterion = criterion
        self.searchType = searchType
        self.sector = sector
        self.ASX_tickerlist = ASX_tickerlist

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
                    if Property == " ".join(row[0].split(" ")[1:]): #ensure "from" and "available" aren't in the word to remove extra net income results
                        tickerProps[ticker].append(Property) 
                        if self.searchType == 2: #if search type is average of all years since 2010 (search type == 2), get average value
                            values = []
                            for value in row[1:]:
                                if not value == "—" and str(value) != "nan":
                                    values.append(round(float(value), 2))
                            if len(values):
                                value = round(statistics.mean(values), 2)
                            else:
                                value = "—"
                        else:
                            value = row[-1] if str(row[-1]) != "nan" else row[-2]
                        self.checkBounds(value, self.criterion[Property]['max'], self.criterion[Property]['min'], self.criterion[Property]['screened'], row[0].split(" ")[0])      
        
        #If the ticker did not have the property listed in the database, do a check anyway on a default "—" value, so that it is still added to the results
        #given there were no criteria entered for that specific property.
        for ticker in tickerProps:
            for Property in self.criterion.keys():
                if not Property in tickerProps[ticker]:
                    self.checkBounds("—", self.criterion[Property]['max'], self.criterion[Property]['min'], self.criterion[Property]['screened'], ticker)

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
        # for name, ticker, sector in pd.read_csv(os.getcwd() + '\\data\\ASXListedCompanies.csv', usecols=[0, 1, 2], header=None).values:
        for name, ticker, sector in pd.read_csv(self.ASX_tickerlist, usecols=[0, 1, 2], header=None).values:
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
        print("ticker list after screen: ", len(screenedTickers))

        rows = []
        for ticker in screenedTickers:
            row = [listings[ticker][0], ticker, listings[ticker][1]]
            for Property in self.criterion.keys():
                row.append(self.criterion[Property]['screened'][ticker])
            rows.append(row)
        return rows
