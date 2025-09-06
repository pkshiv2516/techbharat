import yaml
from pathlib import Path


KB_DIR = Path("data/kb")
REFS = yaml.safe_load(open(KB_DIR/"references.yaml", "r", encoding="utf-8"))


REF_MAP = {r["id"]: r for r in REFS.get("sources", [])}


def map_sources(evidence: list[dict]) -> list[dict]:
    out = []
    for ev in evidence:
        src = REF_MAP.get(ev.get("source"))
        out.append({**ev, "source_detail": src})
    return out