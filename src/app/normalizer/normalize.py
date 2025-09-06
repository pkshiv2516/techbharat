from typing import Dict
from ..parsers.ingredients import canonicalize_ingredients
from ..parsers.nutrition import normalize_nutrition




def normalize_payload(ingredients_text: str | None, nutrition_raw: Dict | None) -> Dict:
    norm = {"ingredients": [], "additive_flags": [], "nutrients": {}}
    if ingredients_text:
        can = canonicalize_ingredients(ingredients_text)
        norm["ingredients"] = can["ingredients"]
        norm["additive_flags"] = can["additive_flags"]
    if nutrition_raw:
        norm["nutrients"] = normalize_nutrition(nutrition_raw)
    norm["additive_flags"] = norm.get("additive_flags", [])
    return norm