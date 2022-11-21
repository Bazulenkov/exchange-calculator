class NotForSendingError(Exception):
    """Base error which we don't send to Telegram."""

    pass


class TelegramError(NotForSendingError):
    """Raise when it was not possible to send message to Telegram.

    We do NOT send this error to Telegram."""

    pass
