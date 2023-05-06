from binance.spot import Spot

import pandas


# Function to get the status
def query_binance_status():
    status = Spot().system_status()
    if status["status"] == 0:
        return True
    else:
        raise ConnectionError


# Function query account
def query_account(api_key, secret_key):
    return Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    ).account()


# query testnet
def query_testnet():
    client = Spot(base_url="https://testnet.binance.vision")
    print(client.time())


# Function to query candlestick data
def get_candlestick_data(symbol, timeframe, qty):
    # get raw data
    raw_data = Spot().klines(symbol=symbol, interval=timeframe, limit=qty)
    converted_data = []

    for candle in raw_data:
        converted_candle = {
            "time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "close_time": candle[6],
            "quote_asset_volume": float(candle[7]),
            "number_of_trades": int(candle[8]),
            "taker_buy_base_asset_volume": float(candle[9]),
            "taker_buy_quote_asset_volume": float(candle[10]),
        }

        # Add the data
        converted_data.append(converted_candle)

    return converted_data


# Function to query all symbols from a base asset
def query_quote_asset_list(quote_asset_symbol):
    symbol_dictionary = Spot().exchange_info()
    # convert this into dataframe
    symbol_dataframe = pandas.DataFrame(symbol_dictionary["symbols"])
    # Extract all the symbols with the base asset pair (ETH)
    quote_symbol_dataframe = symbol_dataframe.loc[
        symbol_dataframe["quoteAsset"] == quote_asset_symbol
    ]
    quote_symbol_dataframe = quote_symbol_dataframe.loc[
        quote_symbol_dataframe["status"] == "TRADING"
    ]
    # ETHSHIBA
    return quote_symbol_dataframe


# Function to make trade with params
def make_trade_with_params(parmas, project_settings):
    print("Making trade with params")
    # Set API key
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["SECRET_KEY"]
    # Create client
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # Make the trade
    try:
        response = client.new_order(**parmas)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")


# Function to query trades
def query_open_trades(project_settings):
    # Set the API Key
    api_key = project_settings["BinanceKeys"]["API_Key"]
    # Set the secret key
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # Setup the client
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # get Trades
    try:
        response = client.get_open_orders()
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")


# Function to cancel a trade
def cancel_order_by_symbol(symbol, project_settings):
    # Set the API Key
    api_key = project_settings["BinanceKeys"]["API_Key"]
    # Set the secret key
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # Setup the client
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )

    # Cancel the trade
    try:
        response = client.cancel_open_orders(symbol=symbol)
        return response
    except ConnectionRefusedError as error:
        print(f"Found error {error}")


# Function to palce a limit order for symbol
def place_limit_order(symbol, side, quantity, price, project_settings):
    # Set the API Key
    api_key = project_settings["BinanceKeys"]["API_Key"]
    # Set the secret key
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # Setup the client
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )

    # Place the limit order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Found error {error}")


def place_stop_loss_order(
    symbol, side, quantity, stop_price, limit_price, project_settings
):
    # Set the API Key
    api_key = project_settings["BinanceKeys"]["API_Key"]
    # Set the secret key
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # Setup the client
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )

    # Place the stop loss order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="STOP_LOSS_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Found error {error}")


def place_take_profit_order(
    symbol, side, quantity, stop_price, limit_price, project_settings
):
    # Set the API Key
    api_key = project_settings["BinanceKeys"]["API_Key"]
    # Set the secret key
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # Setup the client
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )

    # Place the take profit order
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Found error {error}")
