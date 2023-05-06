from flask import Flask, request
from moralis import evm_api
from dotenv import load_dotenv
import execute
import datetime
import locale
import os
import json

load_dotenv()

api_key = os.getenv("MORALIS_API_KEY")

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
app = Flask(__name__)


@app.route("/getPrice", methods=["GET"])
def prices():
    address = request.args.get("address")
    chain = request.args.get("chain")
    params = {
        "chain": chain,
        "exchange": "pancakeswap-v2",
        "address": address,
    }

    result = evm_api.token.get_token_price(
        api_key=api_key,
        params=params,
    )

    return result


@app.route("/webhook", methods=["POST"])
def webhook():
    webhook = request.data.decode("utf-8")
    json_object = json.loads(webhook)

    txs = json_object["txs"]
    for tx in txs:
        from_address = tx["fromAddress"]
        to_address = tx["toAddress"]

        whale = "Your whale"
        whale = whale.lower()
        if from_address == whale:
            print("sell")
            execute.execute_analysis_and_trade("sell")

        elif to_address == whale:
            print("buy")
            execute.execute_analysis_and_trade("buy")

        else:
            print("no whale")

    return "ok"


if __name__ == "__main__":
    app.run(port=5002, debug=True)
