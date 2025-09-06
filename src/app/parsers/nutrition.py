from typing import Dict


KEY_MAP = {
    "sugars": "sugars_100g",
    "sugar": "sugars_100g",
    "salt": "salt_100g",
    "sodium": "salt_100g",
    "saturated fat": "saturated_fat_100g",
    "saturated_fat": "saturated_fat_100g",
    "protein": "proteins_100g",
    "fiber": "fiber_100g",
    "fibre": "fiber_100g",
    "fat": "fat_100g",
    "trans fat": "trans_fat_100g",
    }




def coerce_float(x):
    try:
        return float(str(x).replace(",", ".").strip())
    except Exception:
        return None




def normalize_nutrition(raw: Dict) -> Dict:
    out = {}
    for k, v in raw.items():
        key = KEY_MAP.get(k.strip().lower())
        if key:
            val = coerce_float(v)
            if val is not None:
                out[key] = val
    if "trans_fat_100g" in out and "fat_100g" in out and out["fat_100g"]:
        out["trans_fat_ratio"] = out["trans_fat_100g"] / max(out["fat_100g"], 1e-9)
    else:
        out["trans_fat_ratio"] = 0.0
    out.setdefault("proteins_100g", 0.0)
    out.setdefault("fiber_100g", 0.0)
    return out