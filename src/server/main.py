from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from ..app.agent.graph import build_graph
from ..app.hitl.approval import hitl
from ..app.config import settings
from ..app.observability.otel import init_otel
import base64


load_dotenv()
init_otel()
app = FastAPI(title="Food Rating Agent")
wf = build_graph()


class RateRequest(BaseModel):
    query: str = ""
    barcode: str | None = None
    ingredients_text: str | None = None
    nutrition_raw: dict | None = None
    image_b64: str | None = None


@app.post("/rate")
def rate(body: RateRequest):
    state = {
    "query": body.query,
    "barcode": body.barcode,
    "image_b64": body.image_b64,
    "ingredients_text": body.ingredients_text,
    "nutrition_raw": body.nutrition_raw,
    "intent": "",
    "logs": [],
    "normalized": {},
    "scoring": {},
    "summary": None,
    "action": None,
    "hitl_id": None,
    }
    out = wf.invoke(state)
    return out


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    return {"image_b64": base64.b64encode(content).decode("utf-8")}


class HITLDecision(BaseModel):
    decision: str


@app.post("/hitl/{rid}")
def decide(rid: str, body: HITLDecision, x_hitl_secret: str = Header(default="")):
    if x_hitl_secret != settings.hitl_secret:
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        res = hitl.decide(rid, body.decision) # type: ignore
        return {"id": res.id, "decision": res.decision}
    except KeyError:
        raise HTTPException(status_code=404, detail="not found")


@app.get("/hitl/{rid}")
def get_decision(rid: str, x_hitl_secret: str = Header(default="")):
    if x_hitl_secret != settings.hitl_secret:
        raise HTTPException(status_code=401, detail="unauthorized")
    try:
        res = hitl.get(rid)  # type: ignore
        return {"id": res.id, "decision": res.decision}
    except KeyError:
        raise HTTPException(status_code=404, detail="not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
