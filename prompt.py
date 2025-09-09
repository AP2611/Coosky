from typing import Optional


SYSTEM_PROMPT = (
    "You are a helpful culinary assistant. Given the user's available ingredients, "
    "suggest several dishes that could be prepared. For each dish, include: suitability "
    "(perfect/good/possible), missing_ingredients with quantities and reasons if helpful, "
    "full ingredients list with quantities, numbered steps with durations, total time, "
    "difficulty, servings, optional cuisine, and a YouTube URL for a high-quality tutorial. "
    "Prefer using provided ingredients. If insufficient, propose minimal additional items. "
    "Ensure food safety and realistic timings. Keep dishes culturally respectful and concise."
)


def build_user_prompt(
    ingredients_csv: str,
    servings: int,
    diet: Optional[str],
) -> str:
    diet_text = f"Dietary preference: {diet}." if diet else ""
    return (
        f"Ingredients on hand: {ingredients_csv}. Desired servings: {servings}. {diet_text} "
        "Return JSON only following the provided schema."
    )


JSON_SCHEMA_INSTRUCTIONS = (
    "Return strictly valid JSON that conforms to this schema: {\n"
    "  \"dishes\": [\n"
    "    {\n"
    "      \"title\": string,\n"
    "      \"suitability\": one of [\"perfect\", \"good\", \"possible\"],\n"
    "      \"missing_ingredients\": [ { \"name\": string, \"quantity\": string?, \"reason\": string? } ],\n"
    "      \"ingredients\": [ { \"name\": string, \"quantity\": string? } ],\n"
    "      \"steps\": [ { \"description\": string, \"duration_minutes\": number } ],\n"
    "      \"total_time_minutes\": number,\n"
    "      \"difficulty\": string,\n"
    "      \"servings\": number,\n"
    "      \"cuisine\": string?,\n"
    "      \"youtube_url\": string\n"
    "    }\n"
    "  ],\n"
    "  \"notes\": string?\n"
    "}\n"
    "Rules:\n"
    "- Do not include any extra keys or commentary.\n"
    "- Ensure valid JSON (double quotes, no trailing commas).\n"
    "- All durations are integers in minutes.\n"
)


