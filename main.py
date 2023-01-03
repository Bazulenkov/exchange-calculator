"""Send to telegram price of BTCUSDT every minute."""
import asyncio
import logging
import os
import sys
import time

from dotenv import load_dotenv

from binanceclient import BinanceClient
from exceptions import TelegramError
from utils import send_message

RETRY_TIME = 600


def check_tokens(telegram_token, chat_id):
    return bool(telegram_token and chat_id)


async def main():
    logger = logging.getLogger(__name__)
    logger.debug("Bot started")

    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not check_tokens(telegram_token, chat_id):
        message = (
            "There are no mandatory variables of the environment: "
            "TELEGRAM_TOKEN, TELEGRAM_CHAT_ID. The program is forcibly stopped."
        )
        logger.critical(message)
        sys.exit(message)

    args = (telegram_token, chat_id)
    binance_client = BinanceClient()
    message = "{symbol} = {price}"
    symbol = "BTCUSDT"

    while True:
        try:
            task = asyncio.create_task(binance_client.get_trade_price(symbol))
            price = await asyncio.gather(task)

            message_to_send = message.format(symbol=symbol, price=price)
            send_message(message_to_send, *args)
        except TelegramError as e:
            logger.error(e, exc_info=True)
        except Exception as e:
            error_message = f" Сбой в работе программы: {e}"
            send_message(error_message, *args)
        finally:
            logger.info(f"The next check will be in {RETRY_TIME / 60} minutes.")
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    logging.basicConfig(
        format=(
            "%(asctime)s [%(levelname)s] - "
            "(%(filename)s).%(funcName)s:%(lineno)d - %(message)s"
        ),
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    asyncio.run(main())
