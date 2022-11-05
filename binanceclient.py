import logging
import sys
from urllib.parse import urljoin

import requests as requests


class BinanceClient:
    BASE_URL = "https://api.binance.co"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_logger()

    def _init_logger(self):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s] " "%(message)s")
        )
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def _request_to_binance(self, url: str, symbol: str):
        params = {"symbol": symbol, "limit": 1}
        try:
            response = requests.get(urljoin(BinanceClient.BASE_URL, url), params)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error("Failed to retrieve data from target url. Error: {e}")
            raise e
        try:
            return response.json()
        except requests.JSONDecodeError as e:
            self.logger.error(
                "Failed to serialize data from response.json. Code: "
                f"{response.status_code}, error: {e}"
            )
            raise e

    def get_trade_price(self, symbol: str) -> float or None:
        url = "/api/v3/trades"
        data = self._request_to_binance(url, symbol)
        try:
            price = data[0]["price"]
            self.logger.info(f"Price for {symbol} received.")
            return price
        except (IndexError, KeyError) as e:
            self.logger.error(
                "Failed to get price from data. Check format of response.json. "
                f"Error: {e}"
            )
            raise e
