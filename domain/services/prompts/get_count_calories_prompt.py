def get_count_calories_prompt(context: str) -> str:
    return f"""You are a nutrition calculation system.
From the context below, extract all foods and exercises into a valid JSON array. Return ONLY this array with no extra text or explanation.

Context: {context}

Each array item must follow one of these structures:
{{
  "type": "food",
  "name": string,
  "grams": number,
  "calories": number (per 100g of product),
  "fat": number (per 100g),
  "proteins": number (per 100g),
  "carbohydrates": number (per 100g)
}}
or
{{
  "type": "exercise",
  "name": string,
  "calories": number (burned),
  "fat": 0,
  "proteins": 0,
  "carbohydrates": 0
}}

Rules:
- Take your time to think, don't worry
- All numbers, not strings
- Calories: round to 1 decimal
- Macronutrients: round to 2 decimals
- List food & exercise names in Ukrainian, grammatically correct
- Use raw/uncooked values unless cooking method is specified
- If context provides calories/macros, use those
- If grams missing, use typical average for this food
- If brand/company (e.g. "McDonalds", "KFC", "Roshen") is named, use that product’s data from your database
- In case there is no brand or TM (e.g. Twix, Mars, Mcchicken menu), but there is packaging or size words (e.g. "пачка", "маленький", "великий"), use:
  * пачка пельменів = 450г
  * пачка макаронів = 400г
  * пачка печива = 250г
  * пачка чіпсів = 150г
  * маленький = 60% standard, великий = 140%, стандартний/none = 100%

Output ONLY the JSON array.
"""