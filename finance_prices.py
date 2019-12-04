
import datetime as dt
from selenium import webdriver
import requests
from selenium.webdriver.support.ui import Select

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
        self._start_webdriver()

    def _start_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox') # required when running as root user. otherwise you would get no sandbox errors.
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_prices(self):
        if self.website == 'portfolio':
            self.get_prices_from_portfolio()
        elif self.website == 'yahoo':
            self.get_prices_from_yahoo()
        else:
            raise ValueError('website argument should be in the list of {}'.format(list(self._website_options.keys())))

    def get_prices_from_portfolio(self):
        self.driver.get(self._website_options['portfolio'])
        element=Select(self.driver.find_element_by_id('exchange-type'))
        element.select_by_value('shares')
        self.get_available_instruments()

    def get_types(self):
        element=Select(self.driver.find_element_by_id('exchange-type'))
        return [x.get_attribute('value') for x in element.options]

    def get_available_instruments():
        element=Select(self.driver.find_element_by_id('exchange-instruments-selector'))
        return [x.text for x in element.options][1:]


    def get_prices_from_yahoo(self):
        pass


if __name__ == '__main__':
    p = Prices('portfolio')
