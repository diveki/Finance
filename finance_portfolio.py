import pandas as pd
import numpy as np
import os
import datetime as dt
import time
from selenium import webdriver
import requests
import json
from bs4 import BeautifulSoup
from io import StringIO
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def last_not_weekend(tmp):
    while tmp.weekday() > 4:
        tmp = tmp - dt.timedelta(days=1)
    return tmp

def yesterday(no_weekend=False):
    tmp = dt.date.today() - dt.timedelta(days=1)
    if no_weekend:
        return tmp
    else:
        tmp = last_not_weekend(tmp)
        return tmp

def align_dates(df, to='D', start=None, end=None):
    if df.index.name != 'Date':
        if 'Date' not in df.columns:
            raise KeyError('One of the column names must be `Date`!')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    ticker = df.Ticker.unique()
    tmp = pd.DataFrame()
    if not end:
        end = yesterday()
    for tck in ticker:
        if not start:
            start = df[df['Ticker']==tck].index.min()
        new_index = pd.date_range(start=start, end=end, freq=to)
        tmp = pd.concat([tmp, df[df['Ticker']==tck].reindex(new_index, method='ffill')], sort=False)
    return tmp


class InitializeDownload:
    def __init__(self, url, instrument, cat, iid, start, end):
        self.instrument = instrument
        self.start = start
        self.end = end
        self.category = cat
        self.iid = iid
        self.url = url
        self.get_csrf_and_sessionID()

    def get_csrf_and_sessionID(self):
        pass

    def create_payload(self):
        pass

    def initialize_start_date(self):
        pass

    def initialize_end_date(self):
        pass

    def initialize_instrument(self):
        pass

    def initialize_time_range(self):
        pass

    def initialize_output_format(self):
        pass

    def initialize_output_type(self):
        pass

    def _fill_input(self, sid, value):
        inputElement = self.driver.find_element_by_id(sid)
        inputElement.clear()
        time.sleep(0.1)
        inputElement.send_keys(value)
        inputElement.send_keys(Keys.ENTER)

    def _select_options(self, sid, svalue):
        eid = self.driver.find_element_by_id(sid)
        # eid.click()
        element = Select(sid)
        element.select_by_value(svalue)


class InitializeDownload_BET(InitializeDownload):

    def get_csrf_and_sessionID(self):
        self.session = requests.session()
        r = self.session.get(self.url)
        self.cookies = r.cookies.values()[0]
        soup = BeautifulSoup(r.text, 'html.parser')
        self.csrf = soup.select_one('meta[name="_csrf"]')['content']

    def create_payload(self):
        maps = self._bet_category_mapping()
        self.payload = {}
        self.payload['startingValue'] = self.start.strftime('%Y.%m.%d.')
        self.payload['endingValue'] = self.end.strftime('%Y.%m.%d.')
        self.payload['resolution'] = 'DAY_TO_DAY'
        self.payload['market'] = 'PROMPT'
        self.payload['currentCategory'] = self.category
        self.payload['format'] = 'CSV'
        self.payload['type'] = 'DETAILED'
        self.payload['selectionList'] = [{
            'category': maps[self.category],
            'selectedInstruments': [{
                'id': str(self.iid),
                'code': self.instrument
            }]}]

    def initialize_header(self):
        self.header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                'Content-type': 'application/json',
                'Accept': '*/*',
                'Cookie': '_ga=GA1.2.90851370.1575892786; _gid=GA1.2.1695595311.1575892786; JSESSIONID=' + self.cookies + '; _gat=1'
                }
    
    def initialize_url(self):
        self.data_url = 'https://bse.hu/pages/data-download/$rspid0x117390x12/$rihistoricalGenerator?_csrf=' + self.csrf

    def _bet_category_mapping(self):
        r = requests.get('https://bse.hu/pages/data-download/$rspid0x117390x12/$rimainCategory?marketType=prompt')
        if r.status_code == 200:
            prompts = r.json()
            mapping = {list(xx.values())[0]:list(xx.values())[1] for xx in prompts}
            return mapping
        else:
            raise ValueError('requests.get for category mapping did not succeed')


class DataBase:
    _column_order = ['Name', 'Close', 'Volume (#)', 'Volume (ccy)', 'Number of trades', 'Open', 'Low', 'High', 'Currency', 'Average price', 'Capitalization', 'News']
    def __init__(self):
        self.setup_connection()
        self._load_thickers()

    def setup_connection(self):
        pass

    def _load_thickers(self):
        pass

    def list_tickers(self):
        pass

    def update(self):
        pass
   
    def download(self, instrument, start, end):
        pass
     
    def _start_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.
        self.driver = webdriver.Chrome(options=chrome_options)

    def load_history(self, tickers=[]):
        pass

    def _find_latest_dates(self):
        return self.data.reset_index().groupby('Name').last()[['Date']]
    
    def _check_last_dates(self, last_dates):
        y = pd.DataFrame(index=last_dates.index)
        y['Date'] = dt.date.today()
        diff = pd.to_datetime(y.Date) - pd.to_datetime(last_dates.Date)
        ind = diff[diff > dt.timedelta(1)].index
        return last_dates.loc[ind,]
    

    def _initialize_input(self, url, instrument, cat, iid, start, end):
        if 'bse.hu' in url:
            if not hasattr(self, '_initialize'):
                self._initialize = InitializeDownload_BET(url, instrument, cat, iid, start, end)
                self._initialize.initialize_header()
                self._initialize.initialize_url()
            else:
                self._initialize.instrument = instrument
                self._initialize.category = cat
                self._initialize.iid = iid
                self._initialize.start = start
                self._initialize.end = end
            self._initialize.create_payload()
    
    def clean_downloaded_data(self, data_downloaded):
        data_downloaded = data_downloaded.drop(columns='Volume (HUF value)')
        data_downloaded.columns = ['Name', 'Date', 'Close', 'Volume (#)', 'Volume (ccy)', 'Number of trades', 'Open', 'Low', 'High', 'Currency', 'Average price', 'Capitalization']
        data_downloaded['News'] = np.nan 
        return data_downloaded

    def save_updates(self, data_update, fullname, mode='w', header=True):
        data_update.to_csv(fullname, mode=mode, header=header)
        print(f'Update has ben saved to {fullname}')
    
    def set_index2Date(self, df, format = None):
        df.Date = pd.to_datetime(df.Date, format=format)
        df = df.set_index('Date')
        return df

    def add_news(self, ls=[]):
        """
        The method adds a new input to the News column for a given instrument and for a given date. 
        Input: 
            ls:  list of inputs consisting of (instrument, date, news)
                instrument: the ticker of the instrument
                date: date in datetime
                news: strictly string
        """          
        if ls == []:
            print('You need an input to perform the add_news function')
        else:    
            for item in ls:
                self._check_input_format(item)
                qq = self.data[self.data.Name==item[0]].News
                qq[item[1]] = item[2]
                self.data.loc[self.data.Name==item[0], 'News'] = qq
            print('News has been added')

    def _check_input_format(self,d):
        if d[0] not in self.list_tickers():
            raise ValueError('The first element of the input should be a valid ticker name!')
        if type(d[2]) is not str:
            raise TypeError('The third element of the input should be a `string`')
        try:
            pd.to_datetime(d[1])
        except ValueError:
            raise ValueError('The second element should be a valid date time format string or pandas datetime!') 


 

class DataBaseExcel(DataBase):
    _path = './Instruments'
    _tickers_name = 'tickers.xlsx'
    _history_name = 'data.csv'
    _is_up2date = False

    def _load_thickers(self):
        path = os.path.join(self._path, self._tickers_name)
        self.tickers_db = pd.read_excel(path)

    def list_tickers(self):
        return self.tickers_db['Ticker'].to_list()

    def load_history(self, tickers=[]):
        path = os.path.join(self._path, self._history_name)
        if self._history_name.split('.')[1] == 'csv':
            df = pd.read_csv(path)
        elif self._history_name.split('.')[1] == 'xlsx':
            df = pd.read_excel(path)
        else:
            raise ValueError(f'The file extention of {self._history_name} is not csv nor xlsx')
        df = self.set_index2Date(df)        
        if not tickers:
            self.data = df
        else:
            self.data = df[df.Name.isin(tickers)]
        self.data = self.data[self._column_order]

    def update(self, save=True):
        if self._is_up2date:
            print('Data is already up to date')
        else:
            last_dates = self._find_latest_dates() + dt.timedelta(days=1)
            last_dates = self._check_last_dates(last_dates)
            if last_dates.shape[0] == 0:
                print('Data is already up to date')
            else:
                # import pdb; pdb.set_trace()
                newest_dates = [yesterday()] * last_dates.shape[0]
                self.update_input = list(zip(last_dates.index, pd.to_datetime(last_dates.Date), newest_dates))
                self.data_update = pd.DataFrame()
                errors = []
                for item in self.update_input:
                    print(f'Updating: {item[0]}')
                    try:
                        tmp = self.download(item[0], item[1], item[2])
                        self.data_update = pd.concat([self.data_update, tmp], sort=False)
                    except Exception as e:
                        errors.append(e)
                        print(e)
                        print(f'There was an issue with the update of {item[0]}')
                if len(errors) < len(self.update_input):
                    self.data_update = self.set_index2Date(self.data_update, format='%d.%m.%Y.')
                    self.data_update = self.data_update[self._column_order]
                    self.data_update.News = ''
                    self.data = pd.concat([self.data, self.data_update], sort=False)
                    if save:
                        self.save_updates(self.data_update, os.path.join(self._path, self._history_name), mode = 'a', header=False)
                    self._is_up2date = True
                else:
                    print('Did not update the database because of an issue!')
                                
    def download(self, instrument, start, end):
        url = self.tickers_db[self.tickers_db.Ticker == instrument].URL.values[0]
        cat = self.tickers_db[self.tickers_db.Ticker == instrument].Category.values[0]
        iid = self.tickers_db[self.tickers_db.Ticker == instrument].Id.values[0]
        self._initialize_input(url, instrument, cat, iid, start, end)
        r=self._initialize.session.post(self._initialize.data_url, data=json.dumps(self._initialize.payload), headers=self._initialize.header)
        if r.status_code == 200:
            tmp = StringIO(r.text)
            data_downloaded = pd.read_csv(tmp)
            return self.clean_downloaded_data(data_downloaded)
        else:
            raise ValueError('status_code is not 200')

   




class DataBaseDB(DataBase):
    pass


class Price:
    def __init__(self):
        pass

    def load_prices(self, path):
        self.prices = pd.read_excel(path, index_col=0)
        self.prices.index = pd.to_datetime(self.prices.index)


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
        self.instrument['Date'] = pd.to_datetime(self.instrument['Date'])
        self.instrument = self.instrument.set_index('Date')

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
    def __init__(self, trades=None, position=None, start=None, end=None):
        self.start_date = start
        self.end_date = end
        self._trades = trades
        if position:
            self.position=position
        else:
            self.calculate_positions()

    def calculate_positions(self):
        self.position = self._trades.instrument[['Ticker', 'Account', 'Amount']].copy()
        # self.position.loc[:,'Position'] = 1
        self.position['Position'] = self.position.groupby(['Ticker', 'Account']).cumsum()
        self.position=self.position.drop(columns=['Amount'])
        self.position = align_dates(self.position)



class Portfolio:
    def __init__(self):
        pass

    def add_new_position(self, instrument):
        pass
