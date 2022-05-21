from credentials import api_key, api_secret
from textLabel import TextLabel
from binance.client import Client
from binance.helpers import round_step_size
from termcolor import colored
import time

client = Client(api_key, api_secret, testnet=False)
text = TextLabel()

i = 1
while i == 1:
    coin = input(text.inputCoin).upper()
    coinPair = f"{coin}USDT"
    amount = float(input(text.inputAmount))
    percent = float(input(text.inputPercent))

    def get_balance():
        var_balance = client.futures_account_balance()[6]["balance"]
        print(text.starDivider)
        print("Balance: " + colored(var_balance, "red"))
        print(text.starDivider)


    def get_tick_size(symbol):
        info = client.get_symbol_info(symbol)
        for f in info["filters"]:
            if f["filterType"] == "PRICE_FILTER":
                return f["tickSize"]


    def get_entry_price(symbol, side):
        futures = client.futures_position_information(symbol=symbol)
        side = side
        if side == "short":
            for f in futures:
                if f["positionSide"] == "SHORT":
                    return f["entryPrice"]
        elif side == "long":
            for f in futures:
                if f["positionSide"] == "LONG":
                    return f["entryPrice"]


    def get_mark_price(symbol, side):
        futures = client.futures_position_information(symbol=symbol)
        side = side
        if side == "short":
            for f in futures:
                if f["positionSide"] == "SHORT":
                    return f["markPrice"]
        elif side == "long":
            for f in futures:
                if f["positionSide"] == "LONG":
                    return f["markPrice"]

    get_balance()
    tick_size = float(get_tick_size(coinPair))

    def stop_price(side, base):
        open_position_entry_price = get_entry_price(coinPair, side)
        current_market_price = get_mark_price(coinPair, side)
        if side == "short" and base == "position_price":
            stop_short_price = float(open_position_entry_price) * (1 + percent / 100)
            stop_short_price_sized = round_step_size(stop_short_price, tick_size)
            return stop_short_price_sized
        elif side == "long" and base == "position_price":
            stop_long_price = float(open_position_entry_price) * (1 - percent / 100)
            stop_long_price_sized = round_step_size(stop_long_price, tick_size)
            return stop_long_price_sized
        elif side == "short" and base == "market_price":
            stop_short_price = float(current_market_price) * (1 + percent / 100)
            stop_short_price_sized = round_step_size(stop_short_price, tick_size)
            return stop_short_price_sized
        elif side == "long" and base == "market_price":
            stop_long_price = float(current_market_price) * (1 - percent / 100)
            stop_long_price_sized = round_step_size(stop_long_price, tick_size)
            return stop_long_price_sized

    def stop_order(side):
        stop_market_long_order = {
            "symbol": coinPair,
            "side": "BUY",
            "type": "STOP_MARKET",
            "timeInForce": 'GTC',
            "stopPrice": str(stop_price("short", "position_price")),
            "positionSide": "LONG",
            "quantity": amount
        }
        stop_market_short_order = {
            "symbol": coinPair,
            "side": "SELL",
            "type": "STOP_MARKET",
            "timeInForce": 'GTC',
            "stopPrice": str(stop_price("long", "position_price")),
            "positionSide": "SHORT",
            "quantity": amount
        }

        stop_market_m_long_order = {
            "symbol": coinPair,
            "side": "BUY",
            "type": "STOP_MARKET",
            "timeInForce": 'GTC',
            "stopPrice": str(stop_price("short", "market_price")),
            "positionSide": "LONG",
            "quantity": amount
        }
        stop_market_m_short_order = {
            "symbol": coinPair,
            "side": "SELL",
            "type": "STOP_MARKET",
            "timeInForce": 'GTC',
            "stopPrice": str(stop_price("long", "market_price")),
            "positionSide": "SHORT",
            "quantity": amount
        }
        if side == "long":
            return stop_market_long_order
        elif side == "short":
            return stop_market_short_order
        elif side == "m_long":
            return stop_market_m_long_order
        elif side == "m_short":
            return stop_market_m_short_order


    cancel_all_orders = {
        "symbol": coinPair
    }

    open_long_order = {
        "symbol": coinPair,
        "side": "BUY",
        "type": "MARKET",
        "positionSide": "LONG",
        "quantity": amount
    }

    close_long_order = {
        "symbol": coinPair,
        "side": "SELL",
        "type": "MARKET",
        "positionSide": "LONG",
        "quantity": amount
    }

    open_short_order = {
        "symbol": coinPair,
        "side": "SELL",
        "type": "MARKET",
        "positionSide": "SHORT",
        "quantity": amount
    }

    close_short_order = {
        "symbol": coinPair,
        "side": "BUY",
        "type": "MARKET",
        "positionSide": "SHORT",
        "quantity": amount,
    }

    it = 1
    while it == 1:
        try:
            print(text.menu)
            order = input(text.inputLabel)
            print(text.shortDashDivider)

            if order == "s":
                client.futures_create_order(**open_short_order)
                text.printInfoText(text.shortPosition)
                get_balance()

            elif order == "l":
                client.futures_create_order(**open_long_order)
                text.printInfoText(text.longPosition)
                get_balance()

            elif order == "sh":
                client.futures_create_order(**open_short_order)
                time.sleep(0.2)
                try:
                    client.futures_create_order(**stop_order("long"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                    time.sleep(0.2)
                    client.futures_create_order(**close_short_order)

                text.printInfoText(text.shortHedge)
                get_balance()

            elif order == "lh":
                client.futures_create_order(**open_long_order)
                try:
                    client.futures_create_order(**stop_order("short"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                    time.sleep(0.2)
                    client.futures_create_order(**close_long_order)

                text.printInfoText(text.longHedge)
                get_balance()

            elif order == "cs":
                close_short = client.futures_create_order(**close_short_order)
                text.printInfoText(text.shortPositionClosed)
                get_balance()

            elif order == "cl":
                client.futures_create_order(**close_long_order)
                text.printInfoText(text.longPositionClosed)
                get_balance()

            elif order == "hgl":
                try:
                    client.futures_create_order(**stop_order("m_long"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                text.printInfoText(text.longHedge)
                get_balance()

            elif order == "hgs":
                try:
                    client.futures_create_order(**stop_order("m_short"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                text.printInfoText(text.hedgeShortOrder)
                get_balance()

            elif order == "co":
                client.futures_cancel_all_open_orders(**cancel_all_orders)
                text.printInfoText(text.ordersCanceled)
                get_balance()

            elif order == "ns":
                client.futures_create_order(**close_short_order)
                client.futures_create_order(**close_long_order)
                client.futures_create_order(**open_short_order)
                time.sleep(0.2)
                try:
                    client.futures_create_order(**stop_order("long"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                text.printInfoText(text.renewShortLong)
                get_balance()

            elif order == "nl":
                client.futures_create_order(**close_long_order)
                client.futures_create_order(**close_short_order)
                client.futures_create_order(**open_long_order)
                time.sleep(0.2)
                try:
                    client.futures_create_order(**stop_order("short"))
                except Exception as e:
                    print(e)
                    print("Try again!")
                text.printInfoText(text.renewLongShort)
                get_balance()

            elif order == "f":
                it = 0
                print(TextLabel.finishDivider)
                get_balance()

        except Exception as e:
            print(e)

    print(TextLabel.continueText)
    x = input()
    if x == "n":
        i = 0

print(TextLabel.gameOverDivider)
