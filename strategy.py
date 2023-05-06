import pandas
import numpy
import binance_connect
import time
import requests


# Function to convert the data from binance candlestick data to a dataframe
def get_and_transform_data(symbol, timeframe, number_of_candles):
    raw_data = binance_connect.get_candlestick_data(
        symbol, timeframe, number_of_candles
    )

    df = pandas.DataFrame(raw_data)
    df["time"] = pandas.to_datetime(df["time"], unit="ms")
    df["close_time"] = pandas.to_datetime(df["close_time"], unit="ms")
    df["RedOrGreen"] = numpy.where((df["open"] < df["close"]), "Green", "Red")

    # return de data frame
    return df


# Get the token price
def get_token_price(address, chain):
    # Make API call to get the price
    url = f"http://localhost:5002/getPrice?address={address}&chain={chain}"
    response = requests.get(url)
    data = response.json()
    # Extract the price

    usd_price = data["usdPrice"]

    return usd_price


# Check the pair relation
def check_pair_relation(address1, address2, chain):
    price1 = get_token_price(address1, chain)
    price2 = get_token_price(address2, chain)

    # Calculate ratio of the prices
    ratio = price1 / price2

    return ratio


def check_ratio_ralation(current_ratio, reference_ratio):
    # Calculate the difference between the ratios
    # Ratio 1 = TOKEN1/TOKEN3
    # Ratio 2 = TOKEN2/TOKEN3
    if current_ratio > reference_ratio:
        # The current ratio is overvalued relative to the reference ratio
        # Consider Selling TOKEN1 for TOKEN3
        return False
    elif current_ratio < reference_ratio:
        # The current ratio is undervalued relative to the reference ratio
        # Consider Buying TOKEN1 with TOKEN3
        return True


# Function to check the consecutive raise or drecrease
def determine_trade_event(symbol, timeframe, percentage_change, candle_color):
    candlestick_data = get_and_transform_data(symbol, timeframe, 3)
    # Review if the candles has the same color
    if (
        candlestick_data.loc[0, "RedOrGreen"] == candle_color
        and candlestick_data.loc[1, "RedOrGreen"] == candle_color
        and candlestick_data.loc[1, "RedOrGreen"] == candle_color
    ):
        # Determine the percentage change
        change_one = determine_percent_change(
            candlestick_data.loc[0, "open"], candlestick_data.loc[0, "close"]
        )
        change_two = determine_percent_change(
            candlestick_data.loc[1, "open"], candlestick_data.loc[1, "close"]
        )
        change_three = determine_percent_change(
            candlestick_data.loc[2, "open"], candlestick_data.loc[2, "close"]
        )

        if candle_color == "Red":
            print(f"First Drop: {change_one}")
            print(f"Second Drop: {change_two}")
            print(f"Third Drop: {change_three}")
        elif candle_color == "Green":
            print(f"First Increase: {change_one}")
            print(f"Second Increase: {change_two}")
            print(f"Third Increase: {change_three}")

        # Compare the price changes agains stated percentage change

        # The minimun treshold of increase or decrease we want to see in the price
        # in order to make the sell/buy decision worth it
        if (
            change_one >= percentage_change
            and change_two >= percentage_change
            and change_three >= percentage_change
        ):
            # We can trade
            return True
        else:
            # We can't trade
            return False
    else:
        # We can't trade
        return False


def determine_percent_change(close_previous, close_current):
    return (close_current - close_previous) / close_previous


def analyze_symbols(symbol_dataframe, timeframe, percentage, type):
    # Iterate trough the symbols
    for index in symbol_dataframe.index:
        # Analyze symbol
        if type == "buy":
            analysis = determine_trade_event(
                symbol=symbol_dataframe["symbol"][index],
                timeframe=timeframe,
                percentage_change=percentage,
                candle_color="Green",
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive rises')
            else:
                print(
                    f'{symbol_dataframe["symbol"][index]} does not have 3 consecutive rises'
                )
            # sleep 1 sec
            time.sleep(1)
            return analysis
        elif type == "sell":
            analysis = determine_trade_event(
                symbol=symbol_dataframe["symbol"][index],
                timeframe=timeframe,
                percentage_change=percentage,
                candle_color="Red",
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive drops')
            else:
                print(
                    f'{symbol_dataframe["symbol"][index]} does not have 3 consecutive drops'
                )
            # sleep 1 sec
            time.sleep(1)
            return analysis


# Buying Params
def calculate_buy_params(symbol, pair, timeframe):
    # Retrieve the las candle
    raw_data = binance_connect.get_candlestick_data(
        symbol=symbol, timeframe=timeframe, qty=1
    )

    # Determine the precision required on the symbol
    precision = pair.iloc[0]["baseAssetPrecision"]
    # Filters
    filters = pair.iloc[0]["filters"]
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            step_size = float(f["stepSize"])
            min_qty = float(f["minQty"])
        elif f["filterType"] == "PRICE_FILTER":
            tick_size = float(f["tickSize"])

    # Extract the clsoe price
    close_price = raw_data[0]["close"]
    print(f"the close price is {close_price}")
    # Calculate the buy stop. This will be 1% of the previous closing price
    buy_stop = close_price * 1.01
    # Round the buy stop price to the nearest valid tick size
    buy_stop = round(buy_stop / tick_size) * tick_size
    # Calculate the quantity. This will be the buy_stop
    raw_quantity = 0.1 / buy_stop
    # Round
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": buy_stop,
        "trailingDelta": 100,
    }

    return params


def calculate_sell_params(symbol, pair, timeframe):
    # Retrieve the last candle
    raw_data = binance_connect.get_candlestick_data(
        symbol=symbol, timeframe=timeframe, qty=1
    )

    # Determine the precision required on for the symbol
    precision = pair.iloc[0]["baseAssetPrecision"]
    print(f"the precision is {precision}")
    # Filters
    filters = pair.iloc[0]["filters"]
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            min_qty = float(f["minQty"])
            step_size = float(f["stepSize"])
            break

    # Extract the close price
    close_price = raw_data[0]["close"]
    print(f"the close price is {close_price}")
    # Calculate the sell stop. This will be 0.99% of the previous closing price
    sell_stop = close_price * 0.99
    print(f"the sell stop is {sell_stop}")
    # Calculate the quantity. This will be 100 / sell_stop
    raw_quantity = 0.1 / sell_stop
    print(f"the raw quantity is {raw_quantity}")
    # Round
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    print(f"the quantity is {quantity}")

    # Create the parameters dictionary based on assumptions
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": close_price,
        "trailingDelta": 100,
    }

    return params
