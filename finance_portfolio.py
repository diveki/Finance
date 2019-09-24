import pandas as pd
import os
import datetime as dt

class Price:
    def __init__(self):
        pass

    def load_prices(self, path):
        self.prices = pd.read_excel(path, index_col=0)
    

class Ticker:
    path = './Instruments'
    filename = 'tickers.xlsx'
    header = ['Name', 'Ticker', 'Currency']

    def __init__(self):
        self.load_tickers()
        
    def load_tickers(self):
        self.ticker = pd.read_excel(os.path.join(self.path, self.filename))
    
    def save_tickers(self, name=None):
        fn = name or self.filename
        fname = os.path.join(self.path, fn)
        self.ticker.to_excel(fname)
        print('Tickers are saved!')
    
    def get_ticker(self, name):
        try:
            nm = self.ticker[self.ticker['Name']==name].Ticker
            return nm.values[0]
        except IndexError:
            print('`{a}` is not a valid identifier. Choose correctly. Try Ticker.ticker!'.format(a=name))
    
    def get_name(self, ticker):
        try:
            tckr = self.ticker[self.ticker['Ticker']==ticker].Name
            return tckr.values[0]
        except IndexError:
            print('`{a}` is not a valid identifier. Choose correctly. Try Ticker.ticker!'.format(a=ticker))

    def get_currency(self, ticker=None, name=None):
        try:
            ccy = self.ticker[(self.ticker['Ticker']==ticker) | (self.ticker['Name']==name)].Currency.values[0]
            return ccy
        except IndexError:
            print('`{a}` or `{b}` is not a valid identifier. Choose correctly. Try Ticker.ticker!'.format(a=ticker, b=name))
    
    def get_instrument_info(self, ticker=None, name=None, ccy=None):
        ccy = self.ticker[(self.ticker['Ticker']==ticker) | (self.ticker['Name']==name) | (self.ticker['Currency']==ccy)]
        return ccy

    def add_tickers(self, td={}):
        if list(td.keys()) != self.header:
            print('The input shoudl contain the following keys: {}'.format(self.header))
        else:
            self.ticker = self.ticker.append(td, ignore_index=True)
    
    def remove_ticker(self, name=None, ticker=None):
        self.ticker = self.ticker[(self.ticker['Name'] != name) & (self.ticker['Ticker'] != ticker)]


class Trades:
    pathname = './Instruments'
    filename = 'trades.xlsx'
    def __init__(self, filename=None):
        fn = self._check_file_path(filename)
        self.load_trades()
    
    def load_trades(self, filename=None):
        fn = self._check_file_path(filename)
        self.instrument = pd.read_excel(fn)
    
    def save_trades(self, filename=None):
        fn = self._check_file_path(filename)
        self.instrument.to_excel(fn)
    
    def _check_file_path(self, filename):
        fn = filename or os.path.join(self.pathname, self.filename)
        return fn

    def __add__(self, other):
        try:
            self.instrument = self.instrument.append(other.instrument, ignore_index=True, sort=False)
        except AttributeError:
            print('Try to use an `Instrument` object as Input!')
    
    def __str__(self):
        return(self.instrument.to_string())


class Instrument:
    instrument_header = ['Date', 'Ticker', 'Amount', 'Price', 'Cost', 'Currency', 'Account']
    def __init__(self, dct, tickerdb=None):
        self.ticker = dct.get('Ticker')
        self.date = dct.get('Date')
        self.amount = dct.get('Amount')
        self.price = dct.get('Price')
        self.cost = dct.get('Cost')
        self.account = dct.get('Account')
        self.currency = tickerdb.get_currency(ticker=dct.get('Ticker')[0])
        dct['Currency'] = self.currency
        self._construct_df(dct)
    
    def _construct_df(self, dct):
        self.instrument = pd.DataFrame(dct)
    
    def __str__(self):
        return('{self.ticker} '.format(self=self))


class Position:
    _start_date = dt.date(2000,1,1)
    _end_date = dt.date.today() - dt.timedelta(days=1)
    def __init__(self, trades=None, position=None, start=None, end=None):
        self.start_date = start or self._start_date
        self.end_date = end or self._end_date
        self._trades = trades
        if position:
            self.position=position
        else:
            self.calculate_positions()
    
    def calculate_positions(self):
        self.position = self._trades.instrument.copy()
        import pdb
        pdb.set_trace()
        rr = pd.date_range(start=self.start_date, end=self.end_date)
        self.position = self.position.set_index('Date').reindex(rr).rename_axis('Date')


class Portfolio:
    def __init__(self):
        pass

    def add_new_position(self, instrument):
        pass