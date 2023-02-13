from enum import Enum
from typing import List
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiologger.loggers.json import JsonLogger


class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class GenericBinanceClient:
    def __init__(self):
        self.logger = JsonLogger.with_default_handlers(
            level="DEBUG",
            serializer_kwargs={"ensure_ascii": False},
        )
        self.session = ClientSession()


class BinanceClient(GenericBinanceClient):
    BASE_URL = "https://api.binance.com"
    LIMIT = 1  # The number of the latest returned data on the symbol

    async def _request_to_binance(self, url: str, symbol: str):
        url = urljoin(self.BASE_URL, url)
        params = {"symbol": symbol, "limit": self.LIMIT}

        async with self.session.get(url=url, params=params) as response:
            return await response.json()

    async def get_trade_price(self, symbol: str) -> float or None:
        url = "/api/v3/trades"
        data = await self._request_to_binance(url, symbol)
        try:
            price = data[0]["price"]
        except (IndexError, KeyError) as e:
            raise e
        self.logger.info(f"Price for {symbol} received.")
        return price


# TODO make Singleton
class P2PBinanceClient(GenericBinanceClient):
    BASE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    PAGE_NUM = 1  # The number of page in response (pagination)
    # ROWS_NUM = 10  # The number of the latest returned data on the symbol
    # FIAT = "RUB"
    # ASSET = "USDT"
    # TRADE_TYPE = "BUY"  # or "SELL" operation for asset

    async def _request_to_p2p_binance(
        self,
        fiat: str,
        trade_type: TradeType,
        asset: str,
        banks: List[str],
        rows_num: int = 1,
    ) -> list:
        # headers = {"user-agent": fake_useragent.UserAgent().random}
        payload = {
            "proMerchantAds": False,
            "page": self.PAGE_NUM,
            "rows": rows_num,
            "payTypes": banks,
            "countries": [],
            "publisherType": None,  # TODO check 'merchant'
            "fiat": fiat,
            "tradeType": trade_type,
            "asset": asset,
            "merchantCheck": False,
        }
        async with self.session.post(url=self.BASE_URL, json=payload) as response:
            response_data = await response.json()
            try:
                return response_data["data"]
            except KeyError as e:
                self.logger.error("Incorrect response", exc_info=True)
                raise e

    def parse_price(self, bucket: list):
        """Return price for first Ads in bucket.

        :param bucket: list of Ads.
        :return: cheapest price
        """
        # result = []
        try:
            # for data in bucket:
            #     result.append(
            #         [
            #             data["adv"]["price"],
            #             data["adv"]["minSingleTransAmount"],
            #             data["adv"]["dynamicMaxSingleTransAmount"],
            #         ]
            #     )
            return bucket[0]["adv"]["price"]
        except KeyError as e:
            self.logger.error("Incorrect response", exc_info=True)
            raise e
        return result

    async def get_exchange_rate(
        self,
        fiat: str,
        asset: str,
        trade_type: str,
        banks: List[str],
        num_rows: int = 1,
    ):
        # if not check_fiat(fiat) or check_asset(asset):
        #     return f"Wrong tiker received: {fiat} or {asset}"
        bucket = await self._request_to_p2p_binance(fiat, trade_type, asset, banks)
        try:
            return self.parse_price(bucket)
        except KeyError as e:
            self.logger.error("Incorrect ", exc_info=True)
            raise e


# if __name__ == "__main__":
#     from tabulate import tabulate
#
#     async def main():
#         p2p_client = P2PBinanceClient()
#         async with p2p_client.session:
#             task = asyncio.create_task(p2p_client.parse_price())
#             result = await task
#             print(tabulate(result, headers=["price", "min_amount", "max_amount"]))
#         # await p2p_client.session.close()
#
#
# asyncio.run(main())
