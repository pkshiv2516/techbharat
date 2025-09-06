from typing import Literal


def route_intent(payload: dict) -> Literal["barcode_lookup", "ocr_only", "kb_recall"]:
    q = (payload.get("query") or "").lower()
    if payload.get("barcode") or "barcode" in q or "ean" in q:
        return "barcode_lookup"
    if payload.get("image") or "ocr" in q:
        return "ocr_only"
    return "kb_recall"