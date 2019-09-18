
import datetime as dt
from selenium import webdriver

class Prices:
    _website_options = {'portfolio':'https://www.portfolio.hu/adatletoltes', 
                        'yahoo'    :''}
    _start = dt.date(1950,1,1)
    _end   = dt.date.today() - dt.timedelta(days=1)

    def __init__(self, website, ins_name=None, start=None, end=None):
        self.website  = website
        self.ins_name = ins_name
        self.start    = start or Prices._start
        self.end      = end or Prices._end
        self.driver   = webdriver.PhantomJS()
    
    def get_prices(self):
        if self.website == 'portfolio':
            self.get_prices_from_portfolio()
        elif self.website == 'yahoo':
            self.get_prices_from_yahoo()
        else:
            raise ValueError('website argument should be in the list of {}'.format(list(self._website_options.keys())))
    
    def get_prices_from_portfolio(self):
        self.driver.get(self._website_options['portfolio'])

    def get_prices_from_yahoo(self):
        pass
