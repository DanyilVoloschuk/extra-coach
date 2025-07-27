import uuid
from typing import Optional, List, Any, Coroutine, Iterable
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import UserChat


class UserChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_chat_by_id(self, user_chat_id: uuid) -> UserChat | None:
        stmt = select(UserChat).where(UserChat.id == user_chat_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_chat(self, filters: dict[str, any] | None = None) -> UserChat:
        stmt = select(UserChat)
        if filters:
            stmt = stmt.filter_by(**{key: value for key, value in filters.items() if getattr(UserChat, key, None)})
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_chats(self, filters: dict[str, any] | None = None) -> Iterable[UserChat]:
        stmt = select(UserChat)
        if filters:
            stmt = stmt.filter_by(**{key: value for key, value in filters.items() if getattr(UserChat, key, None)})
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_user_chat(self, user_chat_data: dict) -> UserChat:
        user_chat = UserChat(**user_chat_data)
        self.db.add(user_chat)
        await self.db.flush()  # Flush to get the ID without committing
        await self.db.refresh(user_chat)
        await self.db.commit()
        return user_chat

    async def update_user_chat(self, filters: dict[str, any], user_chat_data: dict) -> UserChat | None:
        stmt = update(UserChat).filter_by(
            **{key: value for key, value in filters.items() if getattr(UserChat, key, None)}
        ).values(**user_chat_data)
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_user_chat(self, user_chat_id: uuid) -> bool:
        stmt = delete(UserChat).where(UserChat.id == user_chat_id)
        result = await self.db.execute(stmt)
        return result.rowcount() > 0

    async def exists(self, filters: dict[str, any]) -> bool:
        stmt = select(UserChat).filter_by(**filters)
        result = await self.db.execute(stmt)
        return result.first() is not None