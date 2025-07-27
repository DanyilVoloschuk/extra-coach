import os
import tempfile

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update

from application.constants import telegram_menu
from application.errors import UserNotActiveError
from application.services.activity_processor_service import ActivityProcessorService
from application.services.user_processor_service import UserProcessorService
from domain.constants import chat_constants
from domain.services.nutrition_report_service import NutritionReportService
from infrastructure.config.settings import get_settings
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.user_chat_repository import UserChatRepository
from infrastructure.database.repositories.nutritional_data_repository import NutritionalDataRepository
from infrastructure.openai.repositories.openai_repository import OpenAIRepository
from infrastructure.telegram.repositories.bot_repository import TelegramRepository


settings = get_settings()


class TelegramMessageService:

    def __init__(self, db: AsyncSession):
        self._db = db
        self.telegram_repository = TelegramRepository()
        self.openai_repository = OpenAIRepository()
        self.user_repository = UserRepository(db)
        self.user_chat_repository = UserChatRepository(db)
        self.nutritional_data_repository = NutritionalDataRepository(db)
        self.activity_processor_service = ActivityProcessorService(db)
        self.nutrition_report_service = NutritionReportService()
        self.user_processor_service = UserProcessorService(db)

    @staticmethod
    def detect_message_type(message: Update) -> str:
        if message.message:
            if message.message.text:
                if message.message.text.startswith("/"):
                    return "command"
                return "text"
            elif message.message.voice:
                return "voice"
            elif message.message.photo:
                return "photo"
            elif message.message.document:
                return "document"
            elif message.message.video:
                return "video"
            elif message.message.audio:
                return "audio"
            elif message.message.sticker:
                return "sticker"
        elif message.callback_query:
            return "callback_query"
        elif message.inline_query:
            return "inline_query"
        return "unknown"

    async def _reply_to_voice_message(self, update: Update):

        await self._verify_user_is_active(update)
        user_chat = await self.user_chat_repository.get_user_chat(filters={"telegram_chat_id": update.message.chat_id})
        if (
            user_chat.stage not in [
                chat_constants.AWAITING_FOR_AUDIO_FOOD,
                chat_constants.AWAITING_FOR_USER_DATA,
            ]
        ):
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=f"Ти дурак? Перед записом тикни кнопку в меню"
            )
            return

        audio = update.message.voice
        try:
            # Download the audio file
            voice = await self.telegram_repository.get_file(audio.file_id)
            if voice is None:
                await self.telegram_repository.send_message(
                    chat_id=update.message.chat_id,
                    text="Sorry, I couldn't access the voice message. Please try sending it again."
                )
                return

            # Create a specific filename for the voice file
            file_path = os.path.join(settings.VOICE_DIR, f"voice_{audio.file_id}.ogg")
            await voice.download_to_drive(file_path)
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=f"Audio file downloaded successfully!\n"
                     f"Duration: {audio.duration} seconds"
            )
            audio_transcription = await self.openai_repository.transcribe_audio(file_path)

            if user_chat.stage == chat_constants.AWAITING_FOR_AUDIO_FOOD:
                await self.activity_processor_service.process_activities_by_text_ai(
                    update=update,
                    activities_str=audio_transcription,
                )

            if user_chat.stage == chat_constants.AWAITING_FOR_USER_DATA:
                await self.user_processor_service.process_user_data_text_ai(
                    update=update,
                    user_text=audio_transcription,
                )

            await self.user_chat_repository.update_user_chat(
                filters={"telegram_chat_id": update.message.chat_id},
                user_chat_data={"stage": chat_constants.NO_ACTIONS_REQUIRED}
            )

        except Exception as e:
            raise e
            print(f"Error handling voice message: {str(e)}")
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Sorry, there was an error processing your voice message."
            )

    async def _reply_to_photo_message(self, update: Update):
        await self._verify_user_is_active(update)
        user_chat = await self.user_chat_repository.get_user_chat(filters={"telegram_chat_id": update.message.chat_id})
        if user_chat.stage != chat_constants.AWAITING_FOR_PHOTO_FOOD:
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=f"Ти дурак? Перед записом тикни кнопку в меню"
            )
            return

        photo = update.message.photo[-1]

        try:
            # Download the photo file
            photo_obj = await self.telegram_repository.get_file(photo.file_id)
            if photo_obj is None:
                await self.telegram_repository.send_message(
                    chat_id=update.message.chat_id,
                    text="Sorry, I couldn't access the photo. Please try sending it again."
                )
                return

            # Create a filename for the photo
            file_path = os.path.join(settings.PHOTOS_DIR, f"photo_{photo.file_id}.jpg")
            await photo_obj.download_to_drive(file_path)

            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=f"Photo saved successfully!\n"
                     f"Size: {photo.width}x{photo.height}"
            )
            await self.activity_processor_service.process_activities_by_photo_and_text_ai(
                update=update,
                photo_path=file_path,
            )

            # Update chat stage
            await self.user_chat_repository.update_user_chat(
                filters={"telegram_chat_id": update.message.chat_id},
                user_chat_data={"stage": chat_constants.NO_ACTIONS_REQUIRED}
            )

        except Exception as e:
            raise e
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Sorry, there was an error processing your photo."
            )

    async def ensure_user_and_chat_exist(self, update: Update):
        user = await self.user_repository.get_user(
            {"telegram_id": update.message.from_user.id}
        )
        if not user:
            user = await self.user_repository.create_user(
                {
                    "name": update.message.from_user.full_name,
                    "telegram_id": update.message.from_user.id,
                    # "is_active": False,
                    "date_joined": update.message.date,
                    "language": "ukr",
                }
            )

        user_chat = await self.user_chat_repository.get_user_chat(
            {"telegram_chat_id": update.message.chat_id}
        )
        if not user_chat:
            await self.user_chat_repository.create_user_chat(
                {
                    "telegram_chat_id": update.message.chat_id,
                    "user_id": user.id,
                    "stage": chat_constants.AWAITING_FOR_USER_DATA
                }
            )

    async def _change_user_chat_stage_by_update(self, update: Update):
        eat_menu_stage = telegram_menu.ACTIVITY_TO_DOMAIN_STAGE[update.message.text]

        await self.user_chat_repository.update_user_chat(
            filters={"telegram_chat_id": update.message.chat_id},
            user_chat_data={"stage": eat_menu_stage}
        )

        stage_text = chat_constants.STAGE_TO_TEXT.get(eat_menu_stage, "")
        if stage_text:
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=stage_text
            )

        return eat_menu_stage

    async def _reply_to_text_message(self, update: Update):

        await self._verify_user_is_active(update)
        user_chat = await self.user_chat_repository.get_user_chat(
            filters={"telegram_chat_id": update.message.chat_id}
        )

        chat_stage = user_chat.stage
        if chat_stage == chat_constants.AWAITING_FOR_TEXT_FOOD:
            await self.activity_processor_service.process_activities_by_text_ai(
                update=update,
                activities_str=update.message.text,
            )
            await self.user_chat_repository.update_user_chat(
                filters={"telegram_chat_id": update.message.chat_id},
                user_chat_data={"stage": chat_constants.NO_ACTIONS_REQUIRED}
            )

        if user_chat.stage == chat_constants.AWAITING_FOR_USER_DATA:
            await self.user_processor_service.process_user_data_text_ai(
                update=update,
                user_text=update.message.text,
            )

        if update.message.text == telegram_menu.EAT_STATS_TEXT:
            await self.activity_processor_service.send_eating_report(update=update)

        if update.message.text == telegram_menu.START_NEW_DAY_TEXT:
            user = await self.user_repository.get_user({"telegram_id": update.message.from_user.id})
            day_counter = user.day_counter + 1
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Молодець, тримай стату минулого дня"
            )
            await self.activity_processor_service.send_eating_report(update=update)
            await self.user_repository.update_user(
                {
                    "telegram_id": update.message.from_user.id,
                },
                {
                    "day_counter": day_counter,
                },
            )

        if update.message.text == telegram_menu.PROFILE_TEXT:
            user_dto = await self.user_processor_service.get_user_data(update=update)
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=user_dto.user_data_message,
            )

        if update.message.text in telegram_menu.ACTIVITY_MENU:
            chat_stage = await self._change_user_chat_stage_by_update(update)


    async def _reply_to_command(self, update: Update):
        if update.message.text == "/start":
            await self.ensure_user_and_chat_exist(update)
            menu_keyboard = telegram_menu.DEFAULT_MENU
            reply_markup = self.telegram_repository.create_reply_keyboard_markup(
                keyboard=menu_keyboard,
                resize_keyboard=True
            )
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Юзай меню блєать:",
                reply_markup=reply_markup
            )

            await self._verify_user_is_active(update)

        await self._verify_user_is_active(update)
        if update.message.text == "/menu":
            menu_keyboard = telegram_menu.DEFAULT_MENU
            reply_markup = self.telegram_repository.create_reply_keyboard_markup(
                keyboard=menu_keyboard,
                resize_keyboard=True
            )
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Юзай меню блєать:",
                reply_markup=reply_markup
            )
        if update.message.text == "/set_user_data":
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=(
                    "Запиши голосове чи напиши текстом наступну інформацію про себе (чим більше скажеш - тим ефективніше працюватиме бот):\n"
                    "- Зріст в сантиметрах\n"
                    "- Вагу в кілограмах\n"
                    "- Вік\n"
                    "- Стать\n"
                    "- Опиши свій день, яка в тебе активність, можливо ким працюєш, які тренування маєш\n"
                    "- Свою ціль (ріст м'язів, зниження ваги, рекомпозиція)\n"
                ),
            )
            await self.user_chat_repository.update_user_chat(
                filters={"telegram_chat_id": update.message.chat_id},
                user_chat_data={"stage": chat_constants.AWAITING_FOR_USER_DATA}
            )

    async def _verify_user_is_active(self, update: Update):
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})
        if not user or not user.is_active:
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text="Шо ти хочеш дурачок пішов ти нафіг червячок\nМоли адміна про активацію",
            )
            raise UserNotActiveError()

    async def handle_webhook_message(self, message: dict):
        update = self.telegram_repository.de_json(message)
        message_type = self.detect_message_type(update)
        try:

            if update.message.text == "/help":
                await self.telegram_repository.send_message(
                    chat_id=update.message.chat_id,
                    text="Юзай меню блєать (поки цей прікол каже лиш це)",
                )

            elif message_type == "command":
                await self._reply_to_command(update)

            elif message_type == "text":
                await self._reply_to_text_message(update)

            elif message_type == "voice":
                await self._reply_to_voice_message(update)

            elif message_type == "photo":
                await self._reply_to_photo_message(update)

        except UserNotActiveError:
            return

