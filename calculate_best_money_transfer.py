#!/usr/bin/env python
import asyncio
from enum import Enum

from binanceclient import P2PBinanceClient

KORONAPAY_FEE_RUB = 0  # 99
BINANCE_P2P_FEE_ADS_RUB_USDT_PERCENTS = 0.1
BINANCE_P2P_FEE_USDT_USD_PERCENTS = 0.35
CREDO_EXCHANGE_RATE_USD_GEL: float = 2.6370


class KoronaCurrency(Enum):
    GEL = "981"
    USD = "840"


async def get_korona_rate(receiving_currency: KoronaCurrency = KoronaCurrency.USD):
    p2p_client = P2PBinanceClient()
    async with p2p_client.session as session:
        korona_url = "https://koronapay.com/transfers/online/api/transfers/tariffs"
        korona_params = {
            "sendingCountryId": "RUS",
            "sendingCurrencyId": "810",
            "receivingCountryId": "GEO",
            "receivingCurrencyId": receiving_currency.value,
            "paymentMethod": "debitCard",
            "receivingAmount": "10000",
            "receivingMethod": "cash",
            "paidNotificationEnabled": "false",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        }
        async with session.get(
            korona_url, params=korona_params, headers=headers
        ) as response:
            korona_json = await response.json()
            try:
                return korona_json[0]["exchangeRate"]
            except KeyError:
                # TODO loggger.error(korona_json)
                return "Нет данных"


def exchange_rub_usd_via_koronapay(amount_rub: int) -> float:
    amount_usd = (amount_rub - KORONAPAY_FEE_RUB) / KORONAPAY_EXCHANGE_RATE_RUB_USD
    exchange_rate_rub_usd = amount_rub / amount_usd
    return exchange_rate_rub_usd


async def exchange_rub_usd_via_binance_p2p(amount_rub: int) -> float:
    p2p_client = P2PBinanceClient()
    async with p2p_client.session:
        rate_rub_usdt_ask: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "BUY", ["TinkoffNew"]
        )
        rate_rub_usdt_ads: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "SELL", ["TinkoffNew"]
        )

        rate_usdt_usd_ask: str = await p2p_client.get_exchange_rate(
            "USD", "USDT", "SELL", ["CREDOBANK", "TBCbank", "BankofGeorgia"]
        )

        rate_usdt_usd_ads: str = await p2p_client.get_exchange_rate(
            "USD", "USDT", "BUY", ["CREDOBANK", "TBCbank", "BankofGeorgia"]
        )
    amount_usdt_ads: float = (
        amount_rub
        / float(rate_rub_usdt_ads)
        * (1 - BINANCE_P2P_FEE_ADS_RUB_USDT_PERCENTS / 100)
    )
    amount_usdt_ask: float = amount_rub / float(rate_rub_usdt_ask)
    amount_usdt: float = min(amount_usdt_ask, amount_usdt_ads)

    amount_usd_ask: float = amount_usdt * float(rate_usdt_usd_ask)
    amount_usd_ads: float = (
        amount_usdt
        * float(rate_usdt_usd_ads)
        * (1 - BINANCE_P2P_FEE_USDT_USD_PERCENTS / 100)
    )
    amount_usd: float = min(amount_usd_ask, amount_usd_ads)

    exchange_rate_rub_usd: float = amount_rub / amount_usd
    return exchange_rate_rub_usd


async def exchange_rub_gel_via_binance_p2p(amount_rub: int) -> float:
    p2p_client = P2PBinanceClient()
    async with p2p_client.session:
        rate_rub_usdt_ask: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "BUY", ["TinkoffNew"]
        )
        rate_rub_usdt_ads: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "SELL", ["TinkoffNew"]
        )

        rate_usdt_gel_ask: str = await p2p_client.get_exchange_rate(
            "GEL", "USDT", "SELL", ["CREDOBANK", "TBCbank", "BankofGeorgia"]
        )

        rate_usdt_gel_ads: str = await p2p_client.get_exchange_rate(
            "GEL", "USDT", "BUY", ["CREDOBANK", "TBCbank", "BankofGeorgia"]
        )
    amount_usdt_ads: float = (
        amount_rub
        / float(rate_rub_usdt_ads)
        * (1 - BINANCE_P2P_FEE_ADS_RUB_USDT_PERCENTS / 100)
    )
    amount_usdt_ask: float = amount_rub / float(rate_rub_usdt_ask)
    amount_usdt: float = min(amount_usdt_ask, amount_usdt_ads)

    amount_gel_ask: float = amount_usdt * float(rate_usdt_gel_ask)
    amount_gel_ads: float = amount_usdt * float(rate_usdt_gel_ads)
    amount_gel: float = min(amount_gel_ask, amount_gel_ads)

    exchange_rate_rub_gel: float = amount_rub / amount_gel
    return exchange_rate_rub_gel


def exchange_rub_gel_via_koronapay_credo(
    amount_rub: int, rub_usd_via_koronapay: float, credo_usd_gel: float
) -> float:
    amount_usd = (amount_rub - KORONAPAY_FEE_RUB) / rub_usd_via_koronapay
    amount_gel = amount_usd * credo_usd_gel
    exchange_rate_rub_gel = amount_rub / amount_gel
    return exchange_rate_rub_gel


if __name__ == "__main__":

    async def main():
        amount = 100_000
        task_exchange_rub_usd_via_binance_p2p = asyncio.create_task(
            exchange_rub_usd_via_binance_p2p(amount)
        )
        task_exchange_rub_gel_via_binance_p2p = asyncio.create_task(
            exchange_rub_gel_via_binance_p2p(amount)
        )
        task_exchange_rub_usd_via_koronapay = asyncio.create_task(
            get_korona_rate(KoronaCurrency.USD)
        )
        task_exchange_rub_gel_via_koronapay = asyncio.create_task(
            get_korona_rate(KoronaCurrency.GEL)
        )

        rub_usd_via_binance_p2p: float = await task_exchange_rub_usd_via_binance_p2p
        rub_gel_via_binance_p2p: float = await task_exchange_rub_gel_via_binance_p2p
        rub_usd_via_koronapay: float = await task_exchange_rub_usd_via_koronapay
        rub_gel_via_koronapay: float = await task_exchange_rub_gel_via_koronapay
        rub_gel_via_koronapay_credo: float = exchange_rub_gel_via_koronapay_credo(
            amount, rub_usd_via_koronapay, CREDO_EXCHANGE_RATE_USD_GEL
        )

        print("RUB to USD via Koronapay: ", rub_usd_via_koronapay)
        print("RUB to USD via Binance: ", rub_usd_via_binance_p2p)
        print("RUB to GEL via Koronapay: ", rub_gel_via_koronapay)
        print("RUB to GEL via Koronapay and Credo: ", rub_gel_via_koronapay_credo)
        print("RUB to GEL via Binance: ", rub_gel_via_binance_p2p)

    asyncio.run(main())
