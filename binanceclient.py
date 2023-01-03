import asyncio
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiologger.loggers.json import JsonLogger


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


class P2PBinanceClient(GenericBinanceClient):
    BASE_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    ROWS = 1  # The number of the latest returned data on the symbol
    FIAT = "RUB"
    ASSET = "USDT"
    TRADE_TYPE = "BUY"  # or "SELL" operation for asset

    async def parse_price(self):
        # headers = {"user-agent": fake_useragent.UserAgent().random}
        payload = {
            "proMerchantAds": False,
            "page": 1,
            "rows": self.ROWS,
            "payTypes": ["TinkoffNew"],  # TODO add variable
            "countries": [],
            "publisherType": None,  # TODO check 'merchant'
            "fiat": self.FIAT,
            "tradeType": self.TRADE_TYPE,
            "asset": self.ASSET,
            "merchantCheck": False,
        }
        async with self.session.post(url=self.BASE_URL, json=payload) as response:
            response_data = await response.json()
            result = []
            try:
                for data in response_data["data"]:
                    result.append(
                        [
                            data["adv"]["price"],
                            data["adv"]["minSingleTransAmount"],
                            data["adv"]["dynamicMaxSingleTransAmount"],
                        ]
                    )
            except KeyError as e:
                self.logger.error("Incorrect response", exc_info=True)
                raise e
            return result


if __name__ == "__main__":
    from tabulate import tabulate

    async def main():
        p2p_client = P2PBinanceClient()
        task = asyncio.create_task(p2p_client.parse_price())
        result = await task
        print(tabulate(result, headers=["price", "min_amount", "max_amount"]))
        await p2p_client.session.close()


asyncio.run(main())
