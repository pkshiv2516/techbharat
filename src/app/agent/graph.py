from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from ..tools.openfoodfacts import OpenFoodFacts
from ..memory import vector_store as mem
from ..ocr.ocr import read_ingredients
from ..normalizer.normalize import normalize_payload
from ..scoring.engine import score
from ..explain.evidence import map_sources
from ..parsers.barcode import decode_barcode
from ..router import route_intent
from ..hitl.approval import hitl
from ..observability.otel import get_tracer
from ..llm.llm import generate_summary
import base64


class AgentState(TypedDict):
    query: str
    barcode: str | None
    image_b64: str | None
    ingredients_text: str | None
    nutrition_raw: dict | None
    intent: str
    logs: List[str]
    normalized: dict
    scoring: dict
    summary: str | None
    action: str | None
    hitl_id: str | None


OFF = OpenFoodFacts()
tracer = get_tracer()




def node_route(s: AgentState):
    s["intent"] = route_intent(s)
    s["logs"].append(f"Intent: {s['intent']}")
    return s




def node_ingest(s: AgentState):
    with tracer.start_as_current_span("ingest"):
        if not s.get("barcode") and s.get("image_b64"):
            try:
                img = base64.b64decode(s["image_b64"]) # may be ingredient photo too
                bc = decode_barcode(img)
                if bc:
                    s["barcode"] = bc
                    s["logs"].append(f"Decoded barcode: {bc}")
            except Exception:
                pass
        if s.get("barcode"):
            try:
                prod = OFF.get_barcode(s["barcode"]) # dict
                nutr = (prod.get("product", {}).get("nutriments", {}))
                ingredients_txt = prod.get("product", {}).get("ingredients_text")
                s["nutrition_raw"] = nutr
                s["ingredients_text"] = ingredients_txt or s.get("ingredients_text")
                s["logs"].append("Fetched from OpenFoodFacts")
            except Exception as e:
                s["logs"].append(f"OFF fetch failed: {e}")
        if s.get("image_b64") and not s.get("ingredients_text"):
            try:
                txt = read_ingredients(base64.b64decode(s["image_b64"]))
                s["ingredients_text"] = txt
                s["logs"].append("OCR extracted ingredients")
            except Exception as e:
                s["logs"].append(f"OCR failed: {e}")
    return s

def node_normalize(s: AgentState):
    with tracer.start_as_current_span("normalize"):
        s["normalized"] = normalize_payload(s.get("ingredients_text"), s.get("nutrition_raw"))
        snippets = []
        if s.get("ingredients_text"):
            snippets.append(s["ingredients_text"])
        if s.get("nutrition_raw"):
            snippets.append(str(s["nutrition_raw"]))
        if snippets:
            mem.add_docs(snippets, metadatas=[{"src":"input"}] * len(snippets))
        return s


LOW_CONF_THRESHOLD = 15

def node_safety(s: AgentState):
    txt = (s.get("ingredients_text") or "").strip()
    if not s.get("nutrition_raw") and len(txt) < LOW_CONF_THRESHOLD:
        req = hitl.create("low_confidence_input", {"reason":"ingredients too short","ingredients_text":txt})
        s["action"] = "PAUSE_HITL"
        s["hitl_id"] = req.id
        s["logs"].append(f"HITL pause created: {req.id}")
    else:
        s["action"] = "PROCEED"
    return s




def node_score_and_summarize(s: AgentState):
    if s.get("action") == "PAUSE_HITL":
        return s
    sc = score(s["normalized"]) # deterministic
    sc["evidence"] = map_sources(sc.get("evidence", []))
    s["scoring"] = sc
    s["logs"].append(f"Score: {sc['score']} Band: {sc['band']}")
    s["summary"] = generate_summary(sc, s.get("normalized", {}))
    return s

def node_final(s: AgentState):
    s["logs"].append("Done")
    return s

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("route", node_route)
    g.add_node("ingest", node_ingest)
    g.add_node("normalize", node_normalize)
    g.add_node("safety", node_safety)
    g.add_node("score_sum", node_score_and_summarize)
    g.add_node("final", node_final)


    g.set_entry_point("route")
    g.add_edge("route", "ingest")
    g.add_edge("ingest", "normalize")
    g.add_edge("normalize", "safety")
    g.add_edge("safety", "score_sum")
    g.add_edge("score_sum", "final")
    g.add_edge("final", END)
    return g.compile()