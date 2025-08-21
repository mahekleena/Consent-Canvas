# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ConsentRequest, ConsentResponse
from backend.ai_logic import negotiate_consent

app = FastAPI(title="ConsentCanvas Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev: allow all; in prod restrict to your extension origin
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"message": "ConsentCanvas backend running"}

@app.post("/negotiate-consent", response_model=ConsentResponse)
def negotiate(data: ConsentRequest):
    decision, decision_map, scores = negotiate_consent(
        banner_text=data.banner_text,
        prefs=data.user_preferences or {}
    )
    return {
        "decision": decision,
        "custom_preferences": decision_map,
        "model_labels": scores
    }
