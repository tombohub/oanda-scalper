import json
import requests
from time import sleep
from decouple import config

API_TOKEN = config(API_TOKEN)
ACCOUNT_ID = config(ACCOUNT_ID)
BASE_URL = "https://api-fxpractice.oanda.com"

# =============================
# IMPORTANT STRATEGY PARAMETERS
RISK_PERCENT = 1

#####
# =============================


def position_size_units(stop_loss, spread):
    """
    position size in lots = risk amount/(stop loss * pip value)
    lot = 100.000 units
    pip value = 10 for USD acount trading xxx/USD pair
    """
    risk_amount = accountBalance()*(RISK_PERCENT/100)
    lots = risk_amount / ((spread + stop_loss) * 10)
    units = lots*100000
    return round(units)


def createMarketOrder(instrument, units, spread=0, stop_loss_pips='', take_profit_price='', trailing_stop=''):
    stop_loss_distance = round((stop_loss_pips+spread)/10000, 5)
    take_profit_price = round(take_profit_price, 5)
    data = {
        "order": {
            "units": units,
            "instrument": instrument,
            "type": "MARKET",
            "takeProfitOnFill": {'price': take_profit_price},
            'stopLossOnFill': {'distance': stop_loss_distance}
        }
    }
    endpoint = BASE_URL + "/v3/accounts/" + ACCOUNT_ID + "/orders"
    header = {"Authorization": "Bearer " + API_TOKEN,
              "Content-Type": "application/json"}
    response = requests.post(
        endpoint,
        headers=header,
        json=data)
    if not response.ok:
        print(json.dumps(response.json(), indent=2))
        #print(response.text, response.status_code)
    else:
        print(json.dumps(response.json(), indent=2))


def openPositions():
    endpoint = BASE_URL + '/v3/accounts/' + ACCOUNT_ID + '/openPositions'
    header = {"Authorization": "Bearer " + API_TOKEN,
              "Content-Type": "application/json"}
    response = requests.get(endpoint, headers=header)
    open_positions = response.json()
    return True if open_positions['positions'] else False


def accountBalance():
    endpoint = BASE_URL + "/v3/accounts/" + ACCOUNT_ID + "/summary"
    header = {'Authorization': 'Bearer ' + API_TOKEN}
    response = requests.get(
        endpoint,
        headers=header,
    )
    account_summary = response.json()
    return float(account_summary['account']['balance'])


""" 
za 1 lot pip value je 10 u drugoj valuti
ako je account u drugoj valuti onda je 10, ako ne onda treba convertirat.
Zato je najlakse imat account u USD

1 lot = 100.000 prve valute
0.1 lot = 10.000 prve valute
0.01 lot = 1.000 prve valute 

Required Account Size = Trade Size u prvoj valuti / Leverage

Risk amount = account size * risk%

likehood of win and losing streak
win%*win%*win%....

"""


def currentPrice(instrument):
    endpoint = BASE_URL + '/v3/accounts/' + ACCOUNT_ID + '/pricing'
    header = header = {'Authorization': 'Bearer ' + API_TOKEN}
    instrument = {'instruments': instrument}
    response = requests.get(endpoint, headers=header, params=instrument)
    price = response.json()
    # print(json.dumps(response.json(), indent=2))
    ask = float(price['prices'][0]['asks'][0]['price'])
    bid = float(price['prices'][0]['bids'][0]['price'])
    spread = round((ask - bid)*10000, 1)
    return {'ask': ask, 'bid': bid, 'spread': spread}


def scalping(instrument, stop_loss_pips, take_profit_pips):
    while True:

        if not openPositions():
            price = currentPrice(instrument)
            spread = price['spread']
            ask = price['ask']
            take_profit_price = ask + take_profit_pips/10000
            units = position_size_units(stop_loss_pips, spread)
            createMarketOrder("GBP_USD", units, spread,
                              stop_loss_pips, take_profit_price)
            print('no open positions')
            print(units)
        else:
            sleep(2)
            print('there is open position')

        # chekirat ima li otvorene pozicije
        # ako nema onda otvorit poziciju sa stop lossom i trailing stopom
        # 2 sekunde pauza, ponovit sve


scalping('GBP_USD', 5, 10)
