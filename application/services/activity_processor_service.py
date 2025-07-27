import os
import tempfile
import uuid
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update

from application.constants import telegram_menu
from domain.constants import chat_constants
from domain.models.nutrition_data import NutritionalData as NutritionalDataDTO
from domain.services.prompts.food_nutritional_data_by_photo import get_food_nutritional_data_by_photo_prompt
from domain.services.prompts.get_count_calories_prompt import get_count_calories_prompt
from domain.services.nutrition_report_service import NutritionReportService
from infrastructure.database.models import NutritionalData
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.user_chat_repository import UserChatRepository
from infrastructure.database.repositories.nutritional_data_repository import NutritionalDataRepository
from infrastructure.openai.repositories.openai_repository import OpenAIRepository
from infrastructure.telegram.repositories.bot_repository import TelegramRepository


class ActivityProcessorService:

    def __init__(self, db: AsyncSession):
        self._db = db
        self.telegram_repository = TelegramRepository()
        self.openai_repository = OpenAIRepository()
        self.user_repository = UserRepository(db)
        self.user_chat_repository = UserChatRepository(db)
        self.nutritional_data_repository = NutritionalDataRepository(db)
        self.nutrition_report_service = NutritionReportService()

    @staticmethod
    def _convert_nutritional_data_to_dto(nutritional_data_list: Iterable[NutritionalData]) -> list[NutritionalDataDTO]:
        return [
            NutritionalDataDTO(
                type=nutritional_data_db.type,
                name=nutritional_data_db.name,
                calories=nutritional_data_db.calories,
                grams=nutritional_data_db.grams,
                fat=nutritional_data_db.fat,
                proteins=nutritional_data_db.proteins,
                carbohydrates=nutritional_data_db.carbohydrates,
            )
            for nutritional_data_db in nutritional_data_list
        ]

    @staticmethod
    def _convert_dict_to_nutritional_data(activity: dict) -> NutritionalData:
        return NutritionalDataDTO(
            type=activity["type"],
            name=activity["name"],
            calories=activity.get("calories") or 0,
            grams=activity.get("grams") or 0,
            fat=activity.get("fat") or 0,
            proteins=activity.get("proteins") or 0,
            carbohydrates=activity.get("carbohydrates") or 0,
        )

    async def process_activities_by_text_ai(self, update: Update, activities_str: str):
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})

        count_calories_prompt = get_count_calories_prompt(activities_str)
        activities = await self.openai_repository.get_json_response(prompt=count_calories_prompt)
        nutritional_report = self.nutrition_report_service.create_nutritional_report(
            [
                self._convert_dict_to_nutritional_data(activity)
                for activity in activities
            ]
        )

        for activity in nutritional_report.activities:
            await self.nutritional_data_repository.create_nutritional_data(
                dict(
                    user_id=user.id,
                    day_counter=user.day_counter,
                    **activity.__dict__,
                )
            )

        await self.telegram_repository.send_message(
            chat_id=update.message.chat_id,
            text=nutritional_report.nutritional_message
        )

    async def process_activities_by_photo_and_text_ai(self, update: Update, photo_path: str):
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})

        caption = update.message.caption
        count_calories_prompt = get_food_nutritional_data_by_photo_prompt(caption)
        activities = await self.openai_repository.get_photo_and_text_json_response(
            prompt=count_calories_prompt,
            image_file_path=photo_path,
        )

        nutritional_report = self.nutrition_report_service.create_nutritional_report(
            [
                self._convert_dict_to_nutritional_data(activity)
                for activity in activities
            ]
        )

        for activity in nutritional_report.activities:
            await self.nutritional_data_repository.create_nutritional_data(
                dict(
                    user_id=user.id,
                    day_counter=user.day_counter,
                    **activity.__dict__,
                )
            )

        await self.telegram_repository.send_message(
            chat_id=update.message.chat_id,
            text=nutritional_report.nutritional_message
        )

    async def send_eating_report(self, update: Update):
        user = await self.user_repository.get_user(filters={"telegram_id": update.message.from_user.id})
        nutritional_data_list = await self.nutritional_data_repository.get_nutritional_data_list(
            filters={"user_id": user.id, "day_counter": user.day_counter}
        )
        nutritional_report = self.nutrition_report_service.create_nutritional_report(
            self._convert_nutritional_data_to_dto(nutritional_data_list)
        )
        await self.telegram_repository.send_message(
            chat_id=update.message.chat_id,
            text=nutritional_report.nutritional_message
        )


