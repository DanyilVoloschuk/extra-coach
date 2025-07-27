import uuid
from dataclasses import dataclass

@dataclass
class User:
   #id: uuid.UUID
    height: float | None = None
    weight: float | None = None
    age: int | None = None
    gender: str = ""
    activity_level: str = ""
    goal: str = ""

    @property
    def filled_changeable_fields(self) -> dict[str, any]:
        fcf = {}

        if self.height:
            fcf["height"] = self.height

        if self.weight:
            fcf["weight"] = self.weight

        if self.age:
            fcf["age"] = self.age

        if self.gender:
            fcf["gender"] = self.gender

        if self.activity_level:
            fcf["activity_level"] = self.activity_level

        if self.goal:
            fcf["goal"] = self.goal

        return fcf

    @property
    def user_data_message(self) -> str:
        text = ""
        if self.height:
            text += f"Зріст: {self.height}\n"

        if self.weight:
            text += f"Вага: {self.weight}\n"

        if self.age:
            text += f"Вік: {self.age}\n"

        if self.gender:
            text += f"Стать: {self.gender}\n"

        if self.activity_level:
            text += f"Денна активність: {self.activity_level}\n"

        if self.goal:
            text += f"Ціль: {self.goal}\n"

        return text if text else "Немає даних про користувача"
