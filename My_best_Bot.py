import time
import requests

# Замените YOUR_TOKEN на ваш токен доступа к API
TOKEN = 't.oHl9rSSAWsqx7CNJGNqB5CcRLjG4Akya_bLwleHLx8SVdFEaLQnnA4HH9dSA43WszCLetIdaun65KLHfDDnXyw'
BROKER_ACCOUNT_ID = 'YOUR_BROKER_ACCOUNT_ID'
BASE_URL = 'https://api-invest.tinkoff.ru/openapi/'

def get_candles(figi, interval, count=1):
    url = BASE_URL + f'market/candles?figi={figi}&interval={interval}&count={count}'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['payload']['candles']

def get_best_prices(figi):
    candles = get_candles(figi, '1min', count=2)
    return candles[0]['c'], candles[1]['c']

def place_market_order(figi, lots, operation):
    url = BASE_URL + 'orders/market-order'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    payload = {
        'figi': figi,
        'brokerAccountId': BROKER_ACCOUNT_ID,
        'lots': lots,
        'operation': operation,
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def main():
    figi = 'BBG000CL9VN6'  # Замените на FIGI акции, которой хотите торговать
    trading_interval = 30  # Интервал торговли в секундах (30 секунд)
    sell_threshold = 1.001  # Порог для продажи на пике высокой цены
    buy_threshold = 0.999  # Порог для покупки на пике низкой цены
    balance = 42.84  # Начальный баланс в рублях
    position = 7.14  # Начальная позиция акций

    while True:
        current_time = time.strftime('%H:%M:%S', time.localtime())
        if '10:00:00' <= current_time <= '18:00:00':
            current_price, prev_price = get_best_prices(figi)
            if current_price >= prev_price * sell_threshold and position > 0:
                response = place_market_order(figi, position, 'Sell')
                print(f'Selling {position} shares at price {current_price}')
                balance += current_price * position
                position = 0
            elif current_price <= prev_price * buy_threshold and balance > 0:
                lots_to_buy = int(balance / current_price)
                response = place_market_order(figi, lots_to_buy, 'Buy')
                print(f'Buying {lots_to_buy} shares at price {current_price}')
                position += lots_to_buy
                balance -= current_price * lots_to_buy
        else:
            print('Outside of trading hours. Waiting...')
        
        time.sleep(trading_interval)

if __name__ == '__main__':
    main()
