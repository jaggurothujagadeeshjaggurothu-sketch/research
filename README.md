# 🔬 ResearchMate AI – Smart Research Assistant (Streamlit)

Turn a rough project idea into **3 research titles, a 150–200 word abstract, 5 keywords,
3 measurable objectives and 3 future enhancements** – 100 % locally with **Ollama + Llama 3.2**.
No OpenAI / paid APIs.

## Features
Dark glassmorphism dashboard · animated loader · per-section Copy / Regenerate / Download ·
Copy-all · one-click PDF export · history · saved projects · input validation ·
JSON validation with automatic retry · missing-model & connection error handling · mobile responsive.

## Structure
```
researchmate-ai/
├── app.py            # Streamlit UI (pages, cards, state)
├── ai_service.py     # Ollama /api/chat integration, system prompt, JSON validation
├── pdf_utils.py      # PDF export (fpdf2)
├── storage.py        # JSON persistence for history
├── styles.py         # CSS + animations
├── requirements.txt
├── .streamlit/config.toml, secrets.toml.example
└── data/             # history.json is created here
```

## 1. Install Ollama + model
1. Install Ollama: https://ollama.com/download
2. Pull the model and make sure the server is running:
```bash
ollama pull llama3.2
ollama serve        # skip if the Ollama app is already running
```

## 2. Run locally (VS Code terminal)
```bash
cd researchmate-ai
python -m venv venv
# Windows:  venv\Scripts\activate        macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501

## 3. Deploy on Streamlit
**Important:** Streamlit Community Cloud runs on Streamlit's servers and **cannot reach `localhost:11434` on your PC**.
Pick one option:

**A. Streamlit Cloud + tunnel to your own Ollama**
1. Run Ollama on your PC and expose it:
   ```bash
   ngrok http 11434 --host-header="localhost:11434"
   ```
   (or `cloudflared tunnel --url http://localhost:11434 --http-host-header localhost:11434`)
2. Push this folder to GitHub → https://share.streamlit.io → *New app* → select `app.py`.
3. App **Settings → Secrets**:
   ```toml
   OLLAMA_URL = "https://your-tunnel-url.ngrok-free.app"
   OLLAMA_MODEL = "llama3.2"
   RESEARCHMATE_PERSIST = "0"
   ```
   Your PC must stay on with Ollama + the tunnel running. Anyone with the URL can use your Ollama, so keep it private.

**B. Run everything on one VM/server (fully self-hosted)**
Install Ollama + `ollama pull llama3.2` on the server, then `streamlit run app.py --server.port 8501` (use Docker/systemd/nginx as you like).
The default URL `http://localhost:11434` then works unchanged.

You can also change the URL/model at runtime in the app: **Settings → Ollama URL**.

## Troubleshooting
| Problem | Fix |
|---|---|
| "Ollama is not reachable" | Run `ollama serve`; check http://localhost:11434 opens ("Ollama is running"). |
| "Model not installed" | `ollama pull llama3.2`; confirm with `ollama list`. |
| Timeout on first request | The model loads into RAM first. Retry, or raise the timeout in Settings. |
| Works locally, fails on Streamlit Cloud | Expected – see section 3 (tunnel or self-host). |
| 403 through ngrok/cloudflared | Keep the `--host-header` / `--http-host-header` flag; or start Ollama with `OLLAMA_ORIGINS=*`. |
| Abstract not 150–200 words | Small models drift; the app retries 3×, then shows a note – click **Regenerate** on the abstract. |
| Slow / out of memory | Close other apps; Llama 3.2 (3B) needs ~4 GB RAM. |
| PDF shows `?` for symbols | The built-in PDF font is Latin-1; unusual symbols are replaced. |
| `streamlit` not found | Activate the venv, `pip install -r requirements.txt`. |

## System prompt
Defined as `SYSTEM_PROMPT` in `ai_service.py`.
