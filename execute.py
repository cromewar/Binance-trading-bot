import json
import os
import binance_connect
import strategy

import_path = "settings.json"


# import settings
def get_settings(import_path):
    # ensure the path exists
    if os.path.exists(import_path):
        file = open(import_path, "r")
        project_settings = json.load(file)
        file.close()
        return project_settings
    else:
        return ImportError


def execute_analysis_and_trade(buy_or_sell):
    project_settings = get_settings(import_path)

    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["SECRET_KEY"]

    ETH = project_settings["Tokens"]["ETH"]
    BTCB = project_settings["Tokens"]["BTCB"]
    BUSD = project_settings["Tokens"]["BUSD"]

    account = binance_connect.query_account(api_key, secret_key)
    if account["canTrade"]:
        print("Your account is ready to trade")

        # Calculate the current ratio
        reference_ratio = strategy.check_pair_relation(ETH, BTCB, "bsc")
        current_ratio = strategy.check_pair_relation(BUSD, BTCB, "bsc")

        print(f"Reference ratio: {reference_ratio}")
        print(f"Current ratio: {current_ratio}")

        # Calculate the difference between the ratios
        check = strategy.check_ratio_ralation(current_ratio, reference_ratio)
        asset_list = binance_connect.query_quote_asset_list("BTC")
        eth_pair = asset_list.loc[asset_list["symbol"] == "ETHBTC"]
        symbol = eth_pair["symbol"].values[0]
        if check and buy_or_sell == "buy":
            print("Buyig Time")
            analysis = strategy.analyze_symbols(eth_pair, "1h", 0.000001, "buy")
            if analysis:
                print("Buying ETH")
                params = strategy.calculate_buy_params(symbol, eth_pair, "1h")
                response = binance_connect.make_trade_with_params(
                    params, project_settings
                )
                print(response)
            else:
                print("Not Buying ETH")
                print(f"Reason: The analysis is {analysis}")
        else:
            if buy_or_sell == "sell":
                print("Selling Time")
                analysis = strategy.analyze_symbols(eth_pair, "1h", 0.000001, "sell")
                if analysis:
                    print("Selling ETH")
                    params = strategy.calculate_sell_params(symbol, eth_pair, "1h")
                    response = binance_connect.make_trade_with_params(
                        params, project_settings
                    )
                    print(response)
                else:
                    print("Not Selling ETH")
                    print(f"Reason: The analysis is {analysis}")
