from domain.models.nutrition_data import NutritionalData, NutritionalDataResult

class NutritionReportService:

    @staticmethod
    def create_nutritional_report(
        food_and_activities: list[NutritionalData],
    ) -> NutritionalDataResult:
        return NutritionalDataResult(food_and_activities)
