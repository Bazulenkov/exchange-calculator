import logging
import sys
from urllib.parse import urljoin

import requests as requests


class BinanceClient:
    BASE_URL = "https://api.binance.co"

    def __init__(self):
        self.logger = logging.getLogger(
            __name__
        )  # Если использовать, то точно не показывать наружу: self._logger
        self._init_logger()

    # ИМХО, логгер стоит таскать с собой тогда, когда нужен полный лог действий
    # Начали запрос, закончил запрос, получили то, это, пятое-десятое. А ради ошибок
    # натыкать везде эти logger.error грязно. Лучше бросать только исключения, а логировать именно ошибки в одном месте
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
            response.raise_for_status()  # элегантно. Но нужно помнить, что оттуда вылетает свой тип исключения, а это зависимость от библиотеки
        except requests.RequestException as e:
            self.logger.error(
                "Failed to retrieve data from target url. Error: {e}"
            )  # тут повторюсь, если цель -- ловить ошибки. То лучше своей исключение бросить с кастомным сообщением. Или использовать расширенный синтаксис
            # raise e
            raise ConnectionError(
                "Some message"
            ) from e  # этот финт ушами убирает зависимость в вызывающем коде от requests. Минус импорт :)
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
            self.logger.info(
                f"Price for {symbol} received."
            )  # а вот и причина тащить с собой логгер :)
            return price  # а это точно нужно внутри try? Тут вообще нужен try?
        # Это моя вкусовщина,вроде бы и по питоньи заворачивать все в try,
        # но можно выкинуть эти все проверки в отдельный метод, который чекнет json из ответа на то,
        # что он не пустой и что там есть нужные ключи. А потом его еще можно и тестами покрыть раздельными.
        except (IndexError, KeyError) as e:
            self.logger.error(
                "Failed to get price from data. Check format of response.json. "
                f"Error: {e}"
            )
            raise e
