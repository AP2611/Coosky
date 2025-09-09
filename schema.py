from typing import List, Optional, Dict, Any, TypedDict


class IngredientSuggestion(TypedDict, total=False):
    name: str
    quantity: Optional[str]
    reason: Optional[str]


class Step(TypedDict):
    description: str
    duration_minutes: int


class Recipe(TypedDict, total=False):
    title: str
    suitability: str
    missing_ingredients: List[IngredientSuggestion]
    ingredients: List[IngredientSuggestion]
    steps: List[Step]
    total_time_minutes: int
    difficulty: str
    servings: int
    cuisine: Optional[str]
    youtube_url: str


class ModelResponse(TypedDict):
    dishes: List[Recipe]
    notes: Optional[str]


def empty_response() -> ModelResponse:
    return {"dishes": [], "notes": ""}


