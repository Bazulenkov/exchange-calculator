import functools
import logging
from typing import Callable, TypeVar, Union

import telegram

logger = logging.getLogger(__name__)

RT = TypeVar("RT")


def log(func: Callable[..., RT], *args: object, **kwargs: object) -> Callable[..., RT]:
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def decorator(*args: object, **kwargs: object) -> RT:
        logger.debug("Entering: %s", func.__name__)
        result = func(*args, **kwargs)
        logger.debug(result)
        logger.debug("Exiting: %s", func.__name__)
        return result

    return decorator


def send_message(
    text: str, tlgm_token: str, chat_id: Union[int, str]
) -> telegram.Message:
    """Send message to telegram chat.

    Args:
        text (:obj:`str`): Text of the message to be sent. Max 4096 characters after
            entities parsing. Also found as :attr:`telegram.constants.MAX_MESSAGE_LENGTH`.
        tlgm_token(:obj:`str`): Bot's unique authentication.
        chat_id (:obj:`int` | :obj:`str`): Unique identifier for the target chat or
            username of the target channel (in the format ``@channelusername``).
    Returns:
        :class:`telegram.Message`: On success, the sent message is returned.
    Raises:
        :class:`telegram.error.TelegramError`
    """
    bot = telegram.Bot(token=tlgm_token)
    posted_message = bot.send_message(chat_id=chat_id, text=text)
    logger.info(f'Message has sent to Telegram: "{text}"')
    return posted_message
