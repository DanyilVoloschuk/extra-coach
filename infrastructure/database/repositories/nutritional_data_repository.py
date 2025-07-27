import uuid
from typing import Optional, List, Any, Coroutine, Iterable
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import NutritionalData


class NutritionalDataRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_nutritional_data_by_id(self, nutritional_data_id: uuid) -> NutritionalData | None:
        stmt = select(NutritionalData).where(NutritionalData.id == nutritional_data_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_nutritional_data_list(self, filters: dict[str, any] | None = None) -> Iterable[NutritionalData]:
        stmt = select(NutritionalData)
        if filters:
            stmt = stmt.filter_by(
                **{key: value for key, value in filters.items() if getattr(NutritionalData, key, None)}
            )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_nutritional_data(self, nutritional_data_data: dict[str, any]) -> NutritionalData:
        nutritional_data = NutritionalData(**nutritional_data_data)
        self.db.add(nutritional_data)
        await self.db.flush()  # Flush to get the ID without committing
        await self.db.refresh(nutritional_data)
        await self.db.commit()
        return nutritional_data

    async def update_nutritional_data(
        self,
        nutritional_data_id: uuid,
        nutritional_data_data: dict[str, any],
    ) -> NutritionalData | None:
        stmt = update(NutritionalData).where(NutritionalData.id == nutritional_data_id).values(**nutritional_data_data)
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_nutritional_data_by_id(nutritional_data_id)

    async def delete_nutritional_data(self, nutritional_data_id: uuid) -> bool:
        stmt = delete(NutritionalData).where(NutritionalData.id == nutritional_data_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount() > 0

    async def exists(self, filters: dict[str, any]) -> bool:
        stmt = select(NutritionalData).filter_by(**filters)
        result = await self.db.execute(stmt)
        return result.first() is not None