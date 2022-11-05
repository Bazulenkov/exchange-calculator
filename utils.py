import logging

import telegram

logger = logging.getLogger(__name__)


def send_message(message: str, tlgm_token, chat_id):
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
        logger.info(f'Message has sent to Telegram: "{message}"')
        return posted_message
    except telegram.error.TelegramError as e:
        logger.error(e)
        raise e
