import os
import tempfile
import uuid
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update

from application.constants import telegram_menu
from domain.constants import chat_constants
from domain.models.nutrition_data import NutritionalData as NutritionalDataDTO
from domain.services.prompts.get_count_calories_prompt import get_count_calories_prompt
from domain.services.nutrition_report_service import NutritionReportService
from domain.services.prompts.get_user_data_prompt import get_user_data_prompt
from domain.services.user_service import UserService
from domain.models.user import User as UserDTO
from infrastructure.database.models import NutritionalData
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.user_chat_repository import UserChatRepository
from infrastructure.database.repositories.nutritional_data_repository import NutritionalDataRepository
from infrastructure.openai.repositories.openai_repository import OpenAIRepository
from infrastructure.telegram.repositories.bot_repository import TelegramRepository


class UserProcessorService:

    def __init__(self, db: AsyncSession):
        self._db = db
        self.telegram_repository = TelegramRepository()
        self.openai_repository = OpenAIRepository()
        self.user_repository = UserRepository(db)
        self.user_chat_repository = UserChatRepository(db)
        self.nutritional_data_repository = NutritionalDataRepository(db)
        self.user_service = UserService()

    async def get_user_data(self, update: Update) -> UserDTO:
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})
        return UserDTO(
            height=user.height,
            weight=user.weight,
            age=user.age,
            gender=user.gender,
            activity_level=user.activity_level,
            goal=user.goal,
        )

    async def process_user_data_text_ai(self, update: Update, user_text: str):
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})
        if not user:
            await self.telegram_repository.send_message(
                chat_id=update.message.chat_id,
                text=f"no user: {update.message.from_user.id}"
            )
            return


        user_data_prompt = get_user_data_prompt(user_text)
        user_data = await self.openai_repository.get_json_response(prompt=user_data_prompt)

        user_dto = self.user_service.convert_dict_to_user(user_data)

        await self.user_repository.update_user({"id": user.id}, user_dto.filled_changeable_fields)
        await self.telegram_repository.send_message(
            chat_id=update.message.chat_id,
            text=user_dto.user_data_message
        )
