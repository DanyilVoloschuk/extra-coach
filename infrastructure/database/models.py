import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


def generate_uuid():
    return uuid.uuid4()


class Language(str, Enum):
    UKR = "ukr"
    ENG = "eng"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    date_joined = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    language = Column(String, default=Language.UKR.value, nullable=False)
    day_counter = Column(Integer, default=0, nullable=False)

    chat = relationship("UserChat", back_populates="user", uselist=False)
    nutritional_data = relationship("NutritionalData", back_populates="user", uselist=True)

    def __str__(self):
        return f"<{self.id}> {self.name}"


class UserChat(Base):
    __tablename__ = "user_chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    telegram_chat_id = Column(Integer, unique=True, nullable=False, index=True)
    stage = Column(String, nullable=False)

    user = relationship("User", back_populates="chat")


class ActivityType(str, Enum):
    FOOD = "food"
    EXERCISE = "exercise"


class NutritionalData(Base):
    __tablename__ = "nutritional_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    date_added = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    grams = Column(Integer, default=0, nullable=False)
    fat = Column(Integer, default=0, nullable=False)
    proteins = Column(Integer, default=0, nullable=False)
    carbohydrates = Column(Integer, default=0, nullable=False)
    day_counter = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="nutritional_data")
