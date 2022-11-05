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
        posted_message = bot.send_message(
            chat_id=chat_id, text=message
        )  # не увидел, что оно используется :)
        logger.info(
            f'Message has sent to Telegram: "{message}"'
        )  # число в учебных целях можно рассказать про else
        return posted_message
    except telegram.error.TelegramError as e:
        logger.error(e)
        raise e  # у нас же зависимость от библиотеки telegram только в этом файле?
    # Если да, то тут точно будет удачнее кинуть свое исключение через raise ... from ..., особенно, если нужно как-то отдельно реагировать на эту ситуацию
    # А тут та самая ситуация. Если функция плюнула исключение, то в main будет провал в блок except Exception,
    # в котором снова попробуем отправить сообщение. При неудаче можно сложить стек =)
