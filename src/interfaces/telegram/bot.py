

from telegram.ext import Application, MessageHandler, filters


class TelegramBot:
    def __init__(self, *, token: str, handlers, bot_name: str) -> None:
        self._token = token
        self._handlers = handlers
        self._bot_name = bot_name

    def run(self) -> None:
        application = Application.builder().token(self._token).build()
        application.add_handler(MessageHandler(filters.VOICE, self._handlers.handle_voice))
        application.add_handler(MessageHandler(filters.PHOTO, self._handlers.handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handlers.handle_text))
        print(f"{self._bot_name} is waking up...")
        application.run_polling()
