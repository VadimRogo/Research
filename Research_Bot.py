import pandas as pd
from binance.client import Client
import talib
import numpy as np
from talib import MA_Type
from talib import ADX, RSI, MACD, STOCH
import datetime
import time
import telebot
from telebot import types
import math

api_key = 'vOpCInjLU7gnTUgIWNbTYIEQSQ7Da77JyUFVMMYyBFCWRo6dmJzwBBKISiPiERfa'
api_secret = 'DG984fylA2GxRcNMQYCaxtHILBKxekGTM6wbLB4yn9z4D14CMZOMhacaSkMlVF8y'

client = Client(api_key, api_secret)
info = client.futures_exchange_info()


partOfBalance = 45

tickets = []

bot = telebot.TeleBot('6312689394:AAE0wejoCqGdUDprRpXjIc401zCmN21SVl4')
id = 1660691311

def sendBought(symbol, takeprofit, stoploss, price):
    bot.send_message(id, f'We bought {symbol} takeprofit {takeprofit} stoploss {stoploss} price now {price}', parse_mode='Markdown')

def sendSold(symbol):
    bot.send_message(id, f"We sold {symbol}", parse_mode='Markdown')

def sendLose(symbol):
    bot.send_message(id, f"We fucked, you need to sell that coin NOW {symbol}")



class passcoin:
    def __init__(self, symbol, dataframe):
        self.symbol = str(symbol)
        self.dataframe = dataframe

class ticket:
    def __init__(self, symbol, price, qty, precision):
        self.symbol = str(symbol)
        self.price = float(price)
        self.qty = float(qty)
        self.takeprofit = price + price / 100
        self.stoploss = price - price / 100
        self.precision = precision
        self.sold = False
        self.percent = price / 100
        self.lenoflife = 0

def get_history_data(coin):
    global result
    client = Client(api_key, api_secret)
    klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    result = pd.DataFrame(klines)
    result = result.rename(columns={0 : 'time', 1 : 'Open', 2 : 'High', 3 : 'Low', 4 : 'Close', 5 : 'Volume', 6 : 'Close time', 7 : 'Quote', 8 : 'Number of trades', 9 : 'Taker buy', 10 : 'Taker buy quote', 11 : 'Ignore'})
    result['time'] = pd.to_datetime(result['time'], unit='ms')
    result['SMA_50'] = talib.SMA(result['Close'])
    result['SMA_100'] = talib.SMA(result['Close'], 100)
    result['SMA_hist'] = result['SMA_50'] - result['SMA_100']
    result['RSI'] = RSI(result['Close'], timeperiod=14)
    result['MACD'], result['Macdsignal'], result['Macdhist'] = MACD(result['Close'], 12, 26, 9)
    result['MACDDay'], result['MacdsignalDay'], result['MacdhistDay'] = MACD(result['Close'], 360, 720, 81)
    result['STOCH'], result['STOCH_k'] = STOCH(result['Close'], result['High'], result['Low'])
    result['ADX'] = ADX(result['High'], result['Low'], result['Close'], timeperiod = 12)
    make_obj_coin(coin, result)
    return result

def get_data(coin):
    try:
        global result
        client = Client(api_key, api_secret)
        klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1MINUTE, "2 minute ago UTC")
        result = pd.DataFrame(klines)
        result = result.rename(columns={0 : 'time', 1 : 'Open', 2 : 'High', 3 : 'Low', 4 : 'Close', 5 : 'Volume', 6 : 'Close time', 7 : 'Quote', 8 : 'Number of trades', 9 : 'Taker buy', 10 : 'Taker buy quote', 11 : 'Ignore'})
        result['SMA_50'] = talib.SMA(result['Close'])
        result['SMA_100'] = talib.SMA(result['Close'], 100)
        result['SMA_hist'] = result['SMA_50'] - result['SMA_100']
        result['RSI'] = RSI(result['Close'], timeperiod=14)
        result['MACD'], result['Macdsignal'], result['Macdhist'] = MACD(result['Close'], 12, 26, 9)
        result['MACDDay'], result['MacdsignalDay'], result['MacdhistDay'] = MACD(result['Close'], 360, 720, 81)
        result['STOCH'], result['STOCH_k'] = STOCH(result['Close'], result['High'], result['Low'])
        result['ADX'] = ADX(result['High'], result['Low'], result['Close'], timeperiod = 12)
        append_last_minute(passcoin, result)
        return result
    except Exception as E:
        print(E)

def update_dataframe(dataframe):
    dataframe['SMA_50'] = talib.SMA(dataframe['Close'])
    dataframe['SMA_100'] = talib.SMA(dataframe['Close'], 100)
    dataframe['SMA_hist'] = dataframe['SMA_50'] - dataframe['SMA_100']
    dataframe['RSI'] = RSI(dataframe['Close'], timeperiod=14)
    dataframe['MACD'], dataframe['Macdsignal'], dataframe['Macdhist'] = MACD(dataframe['Close'], 12, 26, 9)
    dataframe['MACDDay'], dataframe['MacdsignalDay'], dataframe['MacdhistDay'] = MACD(dataframe['Close'], 360, 720, 81)
    dataframe['STOCH'], dataframe['STOCH_k'] = STOCH(dataframe['Close'], dataframe['High'], dataframe['Low'])
    dataframe['ADX'] = ADX(dataframe['High'], dataframe['Low'], dataframe['Close'], timeperiod = 12)
    
def make_obj_coin(coin, dataframe):
    x = passcoin(coin, dataframe)
    passescoins.append(x)

def append_last_minute(obj, dataframe):
    obj.dataframe = pd.concat([obj.dataframe, dataframe], ignore_index=True)

def get_precision(symbol):
   for x in info['symbols']:
       if x['symbol'] == symbol:
         precision = x['quantityPrecision']
         if precision == 0 or precision == None:
             precision = 1
         else:
            precision = int(precision)
         return precision
        
def checkPrecision(price, precision):
    if precision == 0 or precision == None:
        precision = 1
    else:
        precision = int(precision)
    x = round(price, precision)
    return x

def buy(symbol, price):
    global tickets
    precision = get_precision(symbol)
    x = checkPrecision(price, precision)
    qty = partOfBalance / x
    qty = round(qty, precision)
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=qty
    )   
    x = ticket(symbol, price, qty, precision)
    print(f'Bought {symbol} takeprofit {x.takeprofit} stoploss {x.stoploss} price {x.price}')
    tickets.append(x)
    sendBought(symbol, x.takeprofit, x.stoploss, x.price)

def sell(ticket):
    try:
        balance_coin = float(client.get_asset_balance(asset=f"{ticket.symbol.replace('USDT', '')}")['free'])
        balance_usdt = balance_coin * ticket.price
        if balance_usdt > 10:
            order = client.order_market_sell(
                symbol=ticket.symbol,
                quantity=ticket.qty
                )
            print('Sold ', ticket.symbol)
            ticket.sold = True 
            balance = float(client.get_asset_balance(asset='USDT')['free'])
            balances.append(balance)
            sendSold(ticket.symbol)
        else:
            print(f"We can't sell that {ticket.symbol}")
            ticket.sold = True
    except Exception as E:
        balance_coin = float(client.get_asset_balance(asset=f"{ticket.symbol.replace('USDT', '')}")['free'])
        balance_usdt = balance_coin * ticket.price
        if balance_usdt > 10:
            quantity = math.floor(balance_coin * (10 ** ticket.precision) * 0.999) / (10 ** ticket.precision)
            qunatity = round(ticket.qty, ticket.precision)
            errorSell(ticket, quantity)
            balance = float(client.get_asset_balance(asset='USDT')['free'])
            balances.append(balance)

def errorSell(ticket, quantity):
    try:
        order = client.order_market_sell(
            symbol=ticket.symbol,
            quantity=quantity
            )
        print('Sold before error', ticket.symbol)
        ticket.sold = True
        sendSold(ticket.symbol)
        balance = float(client.get_asset_balance(asset='USDT')['free'])
        balances.append(balance)
    except Exception as E:
        print(ticket.symbol)
        print("Okey it doesn't work")
        counter = 0
        balance_coin = float(client.get_asset_balance(asset=f"{ticket.symbol.replace('USDT', '')}")['free'])
        while True:
            try:
                quantity = math.floor(balance_coin * (10 ** ticket.precision) * 0.99) / (10 ** ticket.precision)
                quantity = round(ticket.qty, ticket.precision)
                order = client.order_market_sell(
                    symbol=ticket.symbol,
                    quantity=quantity
                )
                print('sold before error error')
                sendSold(ticket.symbol)
                break
            except:
                counter += 1
                if counter == 5:
                    print('We lose all')
                    print(f'Error qty {quantity}, qty that we have {balance_coin}')
                    sendLose(ticket.symbol)
                    ticket.sold = True
                    break

def Strategy(passcoin):
    global balances, OnPosition, tickets
    price = float(passcoin.dataframe['Close'].iloc[[-1]].iloc[0])
    rsi = float(passcoin.dataframe['RSI'].iloc[[-1]].iloc[0])
    macdhist = float(passcoin.dataframe['Macdhist'].iloc[[-1]].iloc[0])
    adx = float(passcoin.dataframe['ADX'].iloc[[-1]].iloc[0])
    percentMacd = float(passcoin.dataframe['Macdhist'].max()) / 100 * 10
    adxmo = float(passcoin.dataframe['ADX'].iloc[[-2]].iloc[0])
    pastcheckmacd = float(passcoin.dataframe['Macdhist'].iloc[[-4]].iloc[0])
    if macdhist >= -percentMacd and macdhist <= percentMacd and rsi >= 15 and rsi <= 30 and adx > adxmo and OnPosition == False and pastcheckmacd <= 0:
        OnPosition = True
        buy(passcoin.symbol, price)

def CheckTickets(symbol):
    global tickets, OnPosition
    price = float(passcoin.dataframe['Close'].iloc[[-1]].iloc[0])
    rsi = float(passcoin.dataframe['RSI'].iloc[[-1]].iloc[0])
    for ticket in tickets:
        ticket.lenoflife += 1
        if symbol == ticket.symbol:
            if ticket.sold == False and OnPosition == True and ticket.lenoflife % 10 == 0:
                print(f'Wait {ticket.takeprofit} or {ticket.stoploss} price now {price}')
            if ticket.takeprofit < price and rsi >= 20 and rsi <= 65 and ticket.sold == False and OnPosition == True:
                ticket.takeprofit = ticket.takeprofit + ticket.percent
                ticket.stoploss = ticket.stoploss + ticket.percent
            elif ticket.takeprofit < price and ticket.sold == False and OnPosition == True:
                sell(ticket)
                OnPosition = False
                ticket.profit = True
            elif ticket.stoploss > price and ticket.sold == False and OnPosition == True:
                sell(ticket)
                OnPosition = False
                ticket.profit = False
                

passescoins = []
balances = []
coins = ['QNTUSDT', 'SOLUSDT', 'ETHUSDT', 'BNBUSDT', 'DOGEUSDT', 'ADAUSDT', 'LTCUSDT', 'LINKUSDT', 'WOOUSDT', 'MANAUSDT', 'DOTUSDT', 'XRPUSDT', 'GALAUSDT', 'SNXUSDT']
# coins = ['SOLUSDT']
for coin in coins:
    get_history_data(coin)
    
for passcoin in passescoins:
    get_data(passcoin.symbol)
OnPosition = False

print('All fine, we start')
try:
    for i in range(1000):
        for passcoin in passescoins:
            get_data(passcoin.symbol)
            update_dataframe(passcoin.dataframe)
            Strategy(passcoin)
            CheckTickets(passcoin.symbol)
        if i % 180 == 0:
            print(i)
            print('len tickets ', len(tickets))
        time.sleep(60)
except Exception as E:
    print(E)

