def get_food_nutritional_data_by_photo_prompt(context: str = "") -> str:
    additional_explanation = ""
    if context:
        additional_explanation = f"Additional explanation for what is on the photo: {context}"
    return f"""Please analyze the provided image of a food item.
Based on visual assessment, estimate the nutritional data per 100 grams for this meal, including calories, fat, proteins, and carbohydrates.
Also, estimate the approximate weight in grams of the meal.
Return ONLY the following dictionary structure:
[
    {{
    type: food,
    name: <name of the meal>,
    calories: <approximate calories per 100g> as integer,
    grams: <estimated grams> as integer,
    fat: <approximate fat per 100g> as integer,
    proteins: <approximate proteins per 100g> as integer,
    carbohydrates: <approximate carbohydrates per 100g> as integer
    }}
]
Ensure the values are realistic and based purely on the visual assessment
{additional_explanation}
"""
