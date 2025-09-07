import streamlit as st
import requests
import base64
import os


API = f"http://{os.getenv('API_HOST','localhost')}:{os.getenv('API_PORT','8000')}"
HITL_SECRET = os.getenv('HITL_SECRET','change-me')


st.set_page_config(page_title="Packaged Food Rating (Ollama)", layout="centered")
st.title("🥫 Packaged Food Rating — Local Ollama + Streamlit")


with st.sidebar:
    st.markdown("### LLM Settings")
    st.caption("This app is wired to your local Ollama for summaries and embeddings.")
    st.text(f"OLLAMA_HOST: {os.getenv('OLLAMA_HOST','http://10.11.5.175:11434')}")
    st.text(f"CHAT_MODEL: {os.getenv('OLLAMA_CHAT_MODEL','llama3.1:8b')}")
    st.text(f"EMBED_MODEL: {os.getenv('OLLAMA_EMBED_MODEL','nomic-embed-text:latest')}")


with st.form("rate-form"):
    barcode = st.text_input("Barcode (optional)")
    query = st.text_input("Query (optional)", value="Rate this product")
    ingredients_text = st.text_area("Ingredients text (optional)")
    nutr = st.text_area("Nutrition key: value per 100g (JSON)", value='{"sugars": 23, "salt": 1.6, "saturated fat": 6, "protein": 9, "fiber": 2}')
    image = st.file_uploader("Upload ingredients or barcode image (optional)", type=["png","jpg","jpeg"])
    submitted = st.form_submit_button("Run")


if 'image_b64' not in st.session_state:
    st.session_state['image_b64'] = None


if submitted:
    image_b64 = None
    if image is not None:
        content = image.read()
        image_b64 = base64.b64encode(content).decode('utf-8')
        st.session_state['image_b64'] = image_b64
    try:
        nutr_parsed = {} if not nutr.strip() else requests.utils.json.loads(nutr)
    except Exception:
        st.error("Nutrition JSON invalid — ignoring.")
        nutr_parsed = {}
    payload = {
        "query": query,
        "barcode": barcode or None,
        "ingredients_text": ingredients_text or None,
        "nutrition_raw": nutr_parsed or None,
        "image_b64": image_b64 or st.session_state.get('image_b64')
    }
    r = requests.post(f"{API}/rate", json=payload, timeout=120)
    r.raise_for_status()
    st.session_state['last'] = r.json()

if 'last' in st.session_state:
    out = st.session_state['last']
    st.subheader("Logs")
    for l in out.get('logs',[]):
        st.write("- ", l)

    st.subheader("Normalized")
    st.json(out.get('normalized',{}))

    if out.get('action') == 'PAUSE_HITL':
        rid = out.get('hitl_id')
        st.warning(f"Low-confidence input, approval required (ID: {rid})")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve"):
                rr = requests.post(f"{API}/hitl/{rid}", json={"decision":"approved"}, headers={"X-HITL-Secret":HITL_SECRET})
                st.success(rr.json())
        with c2:
            if st.button("Reject"):
                rr = requests.post(f"{API}/hitl/{rid}", json={"decision":"rejected"}, headers={"X-HITL-Secret":HITL_SECRET})
                st.error(rr.json())
    else:
        st.subheader("Score")
        st.metric(label="Health Score", value=out.get('scoring',{}).get('score'), delta=out.get('scoring',{}).get('band'))
        st.subheader("Top Drivers")
        for d in out.get('scoring',{}).get('drivers',[]):
            st.write(f"{d['driver']} (weight {d['weight']}) → value: {d['value']}")
        st.subheader("Evidence (with sources)")
        st.json(out.get('scoring',{}).get('evidence',[]))
        st.subheader("Natural-language Summary (Ollama)")
        st.write(out.get('summary') or "(no summary)")