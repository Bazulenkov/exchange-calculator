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

    # в качестве улучшения можно еще чекать, что токены реально были.
    # пустые строки по умолчанию для токеном в запаре могут сломать мозги :)
    # лучше проверить, что токены не пустые, и если что просто остановится исключением или sys.exit
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    args = (telegram_token, chat_id)
    binance_client = BinanceClient()
    message = "{symbol} = {price}"  # тут и ниже -- это ж настройки. Не хочешь утащить их в файл настроек или на худой конец в константы наверх?
    symbol = "BTCUSDT"
    while True:
        try:
            price = binance_client.get_trade_price(symbol)
            message_to_send = message.format(symbol=symbol, price=price)
            send_message(message_to_send, *args)
        except Exception as e:
            error_message = f" Сбой в работе программы: {e}"
            send_message(error_message, *args)
        time.sleep(1 * 60)  # а тут в число учебных целях можно показать finally.


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] (%(name)s) %(levelname)s: %(message)s",
    )
    main()
