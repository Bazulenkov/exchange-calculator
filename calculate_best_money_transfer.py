#!/usr/bin/env python
import asyncio
import logging
from enum import Enum

import aiohttp
from faker import Faker

from binanceclient import P2PBinanceClient
from configs import configure_logging

BINANCE_RUSSIAN_BANKS = ["TinkoffNew"]

# BINANCE_GEORGIAN_BANKS = ["CREDOBANK", "TBCbank", "BankofGeorgia"]
BINANCE_GEORGIAN_BANKS = ["CREDOBANK", "TBCbank"]

KORONAPAY_FEE_RUB = 0  # 99
BINANCE_P2P_FEE_ADS_RUB_USDT_PERCENTS = 0.1
BINANCE_P2P_FEE_ADS_USDT_USD_PERCENTS = 0.35

CREDO_EXCHANGE_RATE_USD_GEL: float = 2.6670


class KoronaCurrency(Enum):
    GEL = "981"
    USD = "840"


async def get_korona_rate(receiving_currency: KoronaCurrency = KoronaCurrency.USD):
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
    headers = {"User-Agent": Faker().chrome()}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            korona_url, params=korona_params, headers=headers
        ) as response:
            korona_json = await response.json()
            try:
                return korona_json[0]["exchangeRate"]
            except KeyError:
                # TODO loggger.error(korona_json)
                return "Нет данных"


# async def get_contact_rate(receiving_currency: ContactCurrency) -> float:
#     contact_url = "https://online.contact-sys.com/transfer/where"
#     contact_params = {"code": "GE"}
#     headers = {"User-Agent": Faker().chrome()}
#
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(
#                 contact_url, params=contact_params, headers=headers
#             ) as response:
#                 contact_transactiond_id = await response.json()
#                 # contact_rate = parse_contact_rate(contact_html)
#                 return ...
#     except aiohttp.ClientError as ce:
#         raise ContactRateParseError(f"Aiohttp ClientError: {ce}")
#     except json.JSONDecodeError as je:
#         raise ContactRateParseError(f"JSON Decode Error: {je}")
#     except Exception as e:
#         raise ContactRateParseError(f"An unexpected error occurred: {e}")


async def exchange_rub_usd_via_binance_p2p(amount_rub: int) -> float:
    p2p_client = P2PBinanceClient()
    async with p2p_client.session:
        rate_rub_usdt_ask: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "BUY", BINANCE_RUSSIAN_BANKS
        )
        rate_rub_usdt_ads: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "SELL", BINANCE_RUSSIAN_BANKS
        )

        rate_usdt_usd_ask: str = await p2p_client.get_exchange_rate(
            "USD", "USDT", "SELL", BINANCE_GEORGIAN_BANKS
        )

        rate_usdt_usd_ads: str = await p2p_client.get_exchange_rate(
            "USD", "USDT", "BUY", BINANCE_GEORGIAN_BANKS
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
        * (1 - BINANCE_P2P_FEE_ADS_USDT_USD_PERCENTS / 100)
    )
    amount_usd: float = min(amount_usd_ask, amount_usd_ads)

    exchange_rate_rub_usd: float = amount_rub / amount_usd
    return exchange_rate_rub_usd


async def exchange_rub_gel_via_binance_p2p(amount_rub: int) -> float:
    p2p_client = P2PBinanceClient()
    async with p2p_client.session:
        rate_rub_usdt_ask: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "BUY", BINANCE_RUSSIAN_BANKS
        )
        rate_rub_usdt_ads: str = await p2p_client.get_exchange_rate(
            "RUB", "USDT", "SELL", BINANCE_RUSSIAN_BANKS
        )

        rate_usdt_gel_ask: str = await p2p_client.get_exchange_rate(
            "GEL", "USDT", "SELL", BINANCE_GEORGIAN_BANKS
        )

        rate_usdt_gel_ads: str = await p2p_client.get_exchange_rate(
            "GEL", "USDT", "BUY", BINANCE_GEORGIAN_BANKS
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
    configure_logging("calculate_best_money_transfer.log")
    logging.getLogger("faker.factory").setLevel(logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.info("Calculator started")

    async def main():
        amount = 100_000
        # task_exchange_rub_usd_via_binance_p2p = asyncio.create_task(
        #     exchange_rub_usd_via_binance_p2p(amount)
        # )
        # task_exchange_rub_gel_via_binance_p2p = asyncio.create_task(
        #     exchange_rub_gel_via_binance_p2p(amount)
        # )
        task_exchange_rub_usd_via_koronapay = asyncio.create_task(
            get_korona_rate(KoronaCurrency.USD)
        )
        task_exchange_rub_gel_via_koronapay = asyncio.create_task(
            get_korona_rate(KoronaCurrency.GEL)
        )

        # rub_usd_via_binance_p2p: float = await task_exchange_rub_usd_via_binance_p2p
        # rub_gel_via_binance_p2p: float = await task_exchange_rub_gel_via_binance_p2p
        rub_usd_via_koronapay: float = await task_exchange_rub_usd_via_koronapay
        rub_gel_via_koronapay: float = await task_exchange_rub_gel_via_koronapay
        rub_gel_via_koronapay_credo: float = exchange_rub_gel_via_koronapay_credo(
            amount, rub_usd_via_koronapay, CREDO_EXCHANGE_RATE_USD_GEL
        )

        print("RUB to USD via Koronapay: ", rub_usd_via_koronapay)
        # print("RUB to USD via Binance: ", rub_usd_via_binance_p2p)
        print("RUB to GEL via Koronapay: ", rub_gel_via_koronapay)
        print("RUB to GEL via Koronapay and Credo: ", rub_gel_via_koronapay_credo)
        # print("RUB to GEL via Binance: ", rub_gel_via_binance_p2p)

    asyncio.run(main())
