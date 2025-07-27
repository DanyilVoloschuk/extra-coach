from dataclasses import dataclass


@dataclass
class NutritionalData:
    type: str
    name: str
    calories: float = 0
    grams: float = 0
    fat: float = 0
    proteins: float = 0
    carbohydrates: float = 0

    @property
    def gram_based_multiplier(self) -> float:
        return round(self.grams / 100 if self.grams else 1, 2)

    @property
    def nutritional_message(self) -> str:
        res = f"<b>{self.name.capitalize()}</b> "
        if self.type == "food":
            if self.grams:
                res += f"{self.grams} грам "
            res += (
                f"додає <b>{round(self.calories * self.gram_based_multiplier, 2)} ккал</b>, "
                f"де <b>{round(self.proteins * self.gram_based_multiplier, 2)}Б / "
                f"{round(self.fat * self.gram_based_multiplier, 2)}Ж / "
                f"{round(self.carbohydrates * self.gram_based_multiplier, 2)}В</b>"
            )
        else:
            res += f"витрачає {self.calories * self.gram_based_multiplier}"
        return res + "\n"


@dataclass
class NutritionalDataResult:
    activities: list[NutritionalData]

    @property
    def fat(self) -> float:
        return round(sum(
            activity.fat * activity.gram_based_multiplier
            for activity in self.activities
            if activity.type == "food"
        ), 2)

    @property
    def proteins(self) -> float:
        return round(sum(
            activity.proteins * activity.gram_based_multiplier
            for activity in self.activities
            if activity.type == "food"
        ), 2)

    @property
    def carbohydrates(self) -> float:
        return round(sum(
            activity.carbohydrates * activity.gram_based_multiplier
            for activity in self.activities
            if activity.type == "food"
        ), 2)

    @property
    def calories_eaten(self) -> float:
        return round(sum(
            activity.calories * activity.gram_based_multiplier
            for activity in self.activities
            if activity.type == "food"
        ), 1)

    @property
    def calories_burn(self) -> float:
        return round(sum(
            abs(activity.calories)
            for activity in self.activities
            if activity.type == "exercise"
        ), 1)

    @property
    def total_calories(self) -> float:
        return round(self.calories_eaten - self.calories_burn, 1)

    @property
    def food_items(self) -> list[NutritionalData]:
        return [
            activity
            for activity in self.activities
            if activity.type == "food"
        ]

    @property
    def exercise_items(self) -> list[NutritionalData]:
        return [
            activity
            for activity in self.activities
            if activity.type == "exercise"
        ]

    @property
    def nutritional_message(self):
        res = ""
        if self.food_items:
            res += "Те шо ти зжер:\n"
            for activity in self.food_items:
                res += activity.nutritional_message

            res += f"Сумарно: {self.calories_eaten}ккал де {self.proteins}Б / {self.fat}Ж / {self.carbohydrates}В\n\n"


        if self.exercise_items:
            res += "Активність:\n"
            for activity in self.exercise_items:
                res += activity.nutritional_message
            res += f"Сумарно: {self.calories_burn}ккал спалено\n\n"

        res += f"<strong>Результат:</strong> {self.total_calories}ккал\n"
        if self.calories_eaten:
            res += f"<strong>БЖВ:</strong> {self.proteins}Б / {self.fat}Ж / {self.carbohydrates}В\n"

        return res