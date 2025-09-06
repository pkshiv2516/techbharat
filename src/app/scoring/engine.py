import yaml
from typing import Dict, List, Tuple
from pathlib import Path


KB_DIR = Path("data/kb")


with open(KB_DIR/"scoring_rules.yaml", "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)


BASE = CONFIG.get("base_score", 80)
CLAMP = CONFIG.get("clamp", [0,100])
BANDS = CONFIG.get("bands", [])
RULES = CONFIG.get("rules", [])




def _metric_value(norm: Dict, metric: str):
    if metric == "additive_flags":
        return norm.get("additive_flags", [])
    return norm.get("nutrients", {}).get(metric)




def _apply_rule(rule: Dict, norm: Dict):
    v = _metric_value(norm, rule["metric"])
    fired = False
    if v is None:
        return 0, None
    if "op" in rule and "value" in rule:
        if rule["op"] == ">" and v > rule["value"]:
            fired = True
        if rule["op"] == ">=" and v >= rule["value"]:
            fired = True
        if rule["op"] == "<" and v < rule["value"]:
            fired = True
        if rule["op"] == "<=" and v <= rule["value"]:
            fired = True
    if "between" in rule and isinstance(v, (int,float)):
        lo, hi = rule["between"]
        if lo <= v <= hi:
            fired = True
    if "contains_any" in rule and isinstance(v, list):
        if any(x in v for x in rule["contains_any"]):
            fired = True
    if fired:
        ev = {
        "id": rule["id"],
        "driver": rule["driver"],
        "weight": rule["weight"],
        "source": rule["source"],
        "value": v,
        }
        return rule["weight"], ev
    return 0, None




def score(norm: Dict) -> Dict:
    s = BASE
    evidence: List[Dict] = []
    for r in RULES:
        w, ev = _apply_rule(r, norm)
        if ev:
            evidence.append(ev)
            s += w
    s = max(CLAMP[0], min(CLAMP[1], s))
    band = next((b["name"] for b in BANDS if s >= b["min"]), "E")
    drivers = sorted(evidence, key=lambda x: abs(x["weight"]), reverse=True)[:5]
    return {"score": s, "band": band, "drivers": drivers, "evidence": evidence}