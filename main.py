"""Send to telegram price of BTCUSDT every minute."""
import logging
import os
import time

from dotenv import load_dotenv

from binanceclient import BinanceClient
from utils import send_message


def main():
    logger = logging.getLogger(__name__)
    logger.debug("Bot started")

    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    args = (telegram_token, chat_id)
    binance_client = BinanceClient()
    message = "{symbol} = {price}"
    symbol = "BTCUSDT"
    while True:
        try:
            price = binance_client.get_trade_price(symbol)
            message_to_send = message.format(symbol=symbol, price=price)
            send_message(message_to_send, *args)
        except Exception as e:
            error_message = f" Сбой в работе программы: {e}"
            send_message(error_message, *args)
        time.sleep(1 * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] (%(name)s) %(levelname)s: %(message)s",
    )
    main()
