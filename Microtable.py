from binance.client import Client

api_key = 'vOpCInjLU7gnTUgIWNbTYIEQSQ7Da77JyUFVMMYyBFCWRo6dmJzwBBKISiPiERfa'
api_secret = 'DG984fylA2GxRcNMQYCaxtHILBKxekGTM6wbLB4yn9z4D14CMZOMhacaSkMlVF8y'

orders = []

client = Client(api_key, api_secret)

order = client.create_order(
                    symbol='SOLUSDT',
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=0.11
                )
print('BUY')
order = client.order_market_sell(
                symbol='SOLUSDT',
                quantity=0.11
                )
print('SOLD')