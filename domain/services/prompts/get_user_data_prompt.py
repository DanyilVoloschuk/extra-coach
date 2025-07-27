def get_user_data_prompt(context: str) -> str:
    return f"""You are a nutrition data processing system.
    Analyze the provided context and return ONLY a JSON object containing user data.
    Do not include any explanations or additional text.

    Context: {context}

    Rules for JSON response:
    1. Return only a valid JSON object
    2. The object must strictly follow this structure:
    {{
        "height": number (in centimeters) or null,
        "weight": number (in kilograms) or null,
        "age": number (in years) or null,
        "gender": string ("male" or "female") or null,
        "activity_level": string ("sedentary", "lightly_active", "moderately_active", "very_active", "extra_active") or null,
        "goal": string ("maintain", "lose", "gain") or null
    }}

    Requirements:
    - All numerical values must be numbers, not strings
    - Round height and weight to 1 decimal place
    - Age must be a whole number
    - Return ONLY the JSON object, no explanations or additional text
    - Activity levels correspond to:
        * sedentary: little or no exercise
        * lightly_active: light exercise/sports 1-3 days/week
        * moderately_active: moderate exercise/sports 3-5 days/week
        * very_active: hard exercise/sports 6-7 days/week
        * extra_active: very hard exercise/sports and physical job
    """
