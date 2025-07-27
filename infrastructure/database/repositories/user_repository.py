import uuid
from typing import Optional, List, Any, Coroutine, Sequence, Iterable
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: uuid) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user(self, filters: dict[str, any] | None = None) -> User | None:
        stmt = select(User)
        if filters:
            stmt = stmt.filter_by(**{key: value for key, value in filters.items() if getattr(User, key, None)})
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_users(self, filters: dict[str, any] | None = None) -> Iterable[User]:
        stmt = select(User)
        if filters:
            stmt = stmt.filter_by(**{key: value for key, value in filters.items() if getattr(User, key, None)})
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user(self, user_data: dict[str, any]) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        await self.db.commit()
        return user

    async def update_user(self, filters: dict[str, any], user_data: dict[str, any]):
        user_data = {key: value for key, value in user_data.items() if getattr(User, key, None)}
        if not user_data:
            return

        stmt = update(User).filter_by(
            **{key: value for key, value in filters.items() if getattr(User, key, None)}
        ).values(
            **{key: value for key, value in user_data.items() if getattr(User, key, None)}
        )

        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_user(self, user_id: uuid) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount() > 0

    async def exists(self, filters: dict[str, any]) -> bool:
        stmt = select(User).filter_by(**filters)
        result = await self.db.execute(stmt)
        return result.first() is not None