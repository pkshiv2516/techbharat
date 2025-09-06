from ..config import settings


def _chat(messages: list[dict]) -> str:
    if settings.use_ollama:
        from ollama import Client
        client = Client(host=settings.ollama_host)
        res = client.chat(model=settings.ollama_chat_model, messages=messages)
        return res.get('message',{}).get('content','')
    else:
        from openai import OpenAI
        client = OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key)
        res = client.chat.completions.create(model=settings.openai_model, messages=messages)
        return res.choices[0].message.content




def generate_summary(scoring: dict, normalized: dict) -> str:
    score = scoring.get('score')
    band = scoring.get('band')
    drivers = scoring.get('drivers', [])
    bullets = "".join([f"- {d['driver']} (impact {d['weight']})" for d in drivers])
    nutrients = normalized.get('nutrients', {})
    prompt = f"""
    You are a nutrition analyst. Write a concise consumer-friendly summary (max 120 words) of a packaged food's health score.
    Score: {score} (Band {band})
    Top drivers:
    {bullets}
    Key nutrients per 100g: {nutrients}
    Guidelines: Be neutral, avoid medical claims, and suggest simple improvements if relevant.
    """
    return _chat([
    {"role":"system","content":"You are a concise nutrition analyst."},
    {"role":"user","content":prompt}
    ])