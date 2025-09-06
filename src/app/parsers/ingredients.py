import re
from typing import Dict, List


ALIASES = {
    "sugar": ["sucrose", "table sugar"],
    "salt": ["sodium chloride"],
    "fiber": ["dietary fibre", "fibre"],
    }


FLAG_SWEETENERS = {"acesulfame k": "acesulfame_k", "aspartame": "aspartame", "saccharin": "saccharin"}




def canonicalize_ingredients(text: str) -> Dict:
    items = [x.strip() for x in re.split(r",|;|", text.lower()) if x.strip()]
    canonical: List[str] = []
    flags: List[str] = []
    for raw in items:
        name = raw
        for k, vs in ALIASES.items():
            if raw in vs:
                name = k
                break
    canonical.append(name)
    for k,v in FLAG_SWEETENERS.items():
        if k in raw:
            flags.append(v)
    return {"ingredients": canonical, "additive_flags": sorted(list(set(flags)))}