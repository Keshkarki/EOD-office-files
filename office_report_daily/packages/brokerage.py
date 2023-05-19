
#brokerage 5 for all

def brokerage(symbol):
    dict = {
        'NIFTY':5,
        'BANKNIFTY':5,
        'FINNIFTY':5
    }

    return dict[symbol]