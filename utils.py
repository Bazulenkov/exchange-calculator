import logging

import telegram

from exceptions import TelegramError

logger = logging.getLogger(__name__)


def send_message(message: str, tlgm_token: str, chat_id: str) -> telegram.Message:
    """Send message to telegram chat.

    Args:
        message: message to send.
        chat_id: telegram chat_id.
        tlgm_token: token for telegram bot.
    Returns:
        :class:`telegram.Message`: On success, the sent message is returned.
    Raises:
        :class:`telegram.error.TelegramError`
    """
    try:
        bot = telegram.Bot(token=tlgm_token)
        posted_message = bot.send_message(chat_id=chat_id, text=message)
    except telegram.error.TelegramError as e:
        raise TelegramError(f"Ошибка отправки телеграм сообщения: {e}")
    logger.info(f'Message has sent to Telegram: "{message}"')
    return posted_message
