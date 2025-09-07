```bash
# 1) Run Ollama locally and pull models
ollama pull llama3.1:8b
ollama pull nomic-embed-text:latest

# 2) App setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ensure USE_OLLAMA=true in .env

# 3) Backend
python -m uvicorn src.server.main:app --host 0.0.0.0 --port 8000

# 4) UI (Streamlit)
streamlit run src/ui/streamlit_app.py