from ftplib import error_reply
from typing import Any, TYPE_CHECKING
import logging
from naff import Client, Extension, listen
import sentry_sdk

if TYPE_CHECKING:
    from main import Bot

def sentry_filter(event: dict[str, Any], hint: dict[str,Any]):
    if 'log_record' in hint:
        record: logging.LogRecord = hint['log_record']
        if 'dis_snek' in record.name:
            if '/commands/permissions: 403' in record.message:
                return None
            if record.message.startswith('Ignoring exception in '):
                return None
    
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            if isinstance(exc_value, OSError):
                return None
    return event

_default_error_handler = Client.default_error_handler

class Sentry(Extension):
    @listen()
    async def on_startup(self) -> None:
        sentry_sdk.set_context('bot', {
            'name': str(self.bot.user),
            'intents':repr(self.bot.intents),
        })

    def default_error_handler(self, source: str, error: Exception) -> None:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('source', source)
            sentry_sdk.capture_exception(error)
        _default_error_handler(source, error)
    
    Client.default_error_handler = default_error_handler

def setup(bot: Client) -> None:
    token = bot.config.sentry_token
    if not token:
        logging.error('Sentry token not found, disabling Sentry integration')
        return
    sentry_sdk.init(token, before_send=sentry_filter)
    Sentry(bot)