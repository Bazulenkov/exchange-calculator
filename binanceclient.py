import logging
import sys
from urllib.parse import urljoin

import requests as requests


class BinanceClient:
    BASE_URL = "https://api.binance.com"

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._init_logger()

    def _init_logger(self):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s] " "%(message)s")
        )
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)

    @staticmethod
    def _request_to_binance(url: str, symbol: str):
        params = {"symbol": symbol, "limit": 1}
        try:
            response = requests.get(urljoin(BinanceClient.BASE_URL, url), params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise e
        try:
            return response.json()
        except requests.JSONDecodeError as e:
            raise e

    def get_trade_price(self, symbol: str) -> float or None:
        url = "/api/v3/trades"
        data = self._request_to_binance(url, symbol)
        try:
            price = data[0]["price"]
        except (IndexError, KeyError) as e:
            raise e
        self._logger.info(f"Price for {symbol} received.")
        return price
