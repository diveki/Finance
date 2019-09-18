import pandas as pd

class Price:
    def __init__(self):
        pass

    def load_prices(self, path):
        self.prices = pd.read_excel(path, index_col=0)
    

class Instrument:
    def __init__(self, name, date, amount, price, cost, currency='HUF'):
        self.name = name
        self.date = date
        self.amount = amount
        self.price = price
        self.cost = cost
        self.currency = currency
    
    def __str__(self):
        return 'self.name w'.format(self)

class Portfolio:
    def __init__(self):
        pass

    def add_new_position(self, instrument)