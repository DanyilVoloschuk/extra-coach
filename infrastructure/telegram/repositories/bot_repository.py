
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application

from infrastructure.config.settings import get_settings


settings = get_settings()


class TelegramRepository:
    _application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    def __init__(self):
        pass

    def de_json(self, data: dict) -> Update:
        return Update.de_json(data, self._application.bot)

    @staticmethod
    def create_reply_keyboard_markup(
        keyboard: list[list[str]],
        resize_keyboard: bool = False
    ) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=resize_keyboard
        )

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: ReplyKeyboardMarkup | None = None,
    ) -> None:
        await self._application.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    async def get_file(self, file_id):
        return await self._application.bot.get_file(file_id)
