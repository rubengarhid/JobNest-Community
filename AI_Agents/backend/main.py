"""
TalentAI — Servidor Backend
============================
Proxy seguro entre el dashboard y Gemini API.
La API Key vive aquí, nunca en el navegador del usuario.

Deploy GRATIS en:
  - Railway:  railway.app  (500 horas/mes gratis)
  - Render:   render.com   (750 horas/mes gratis)

Variables de entorno necesarias:
  GEMINI_API_KEY=AIza...
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="TalentAI Backend", version="1.0")

# Permite que cualquier navegador llame a este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class ChatRequest(BaseModel):
    system: str
    user: str

@app.get("/")
def root():
    return {"status": "TalentAI backend activo ✓", "model": "gemini-2.0-flash"}

@app.get("/health")
def health():
    return {"ok": True, "key_configured": bool(GEMINI_API_KEY)}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(500, "GEMINI_API_KEY no configurada en el servidor")

    payload = {
        "system_instruction": {"parts": [{"text": req.system}]},
        "contents": [{"role": "user", "parts": [{"text": req.user}]}],
        "generationConfig": {"maxOutputTokens": 1500, "temperature": 0.7}
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload)

    if r.status_code != 200:
        detail = r.json().get("error", {}).get("message", f"Error {r.status_code}")
        raise HTTPException(r.status_code, detail)

    data = r.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return {"text": text}
