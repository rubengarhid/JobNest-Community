"""
TalentAI — Backend híbrido ML + Claude
======================================================
Endpoints:
  POST /predict   → Ejecuta tu modelo sklearn/XGBoost y devuelve el score ML
  POST /chat      → Proxy estándar a Claude (usado por el HTML en MODE='backend')
  POST /analyze   → Pipeline completo: ML score → enriquece prompt → Claude genera informe

Requisitos:
  pip install fastapi uvicorn scikit-learn xgboost joblib anthropic python-dotenv

Variables de entorno (.env):
  ANTHROPIC_API_KEY=sk-ant-...

Arrancar:
  uvicorn backend_ml:app --reload --port 8000
"""

import os
import json
import joblib
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import anthropic

load_dotenv()

# ── Configuración ────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_PATH        = os.getenv("MODEL_PATH", "modelo_talentai.pkl")   # ← ruta a tu .pkl
CLAUDE_MODEL      = "claude-sonnet-4-20250514"

app = FastAPI(title="TalentAI ML Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción, limita a tu dominio
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Carga del modelo ──────────────────────────────────────────────────────────
ml_model = None

def get_model():
    """Carga el modelo la primera vez que se necesita (lazy loading)."""
    global ml_model
    if ml_model is None:
        if not Path(MODEL_PATH).exists():
            raise FileNotFoundError(
                f"Modelo no encontrado en '{MODEL_PATH}'. "
                "Coloca tu .pkl junto a este archivo o ajusta MODEL_PATH en .env"
            )
        ml_model = joblib.load(MODEL_PATH)
    return ml_model


# ── Schemas ───────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    """
    Envía las features que espera tu modelo.
    Adapta los campos a tu caso real.
    """
    years_experience:    float = 0.0   # años de experiencia total
    skills_match:        float = 0.0   # 0-1, % de skills requeridas que tiene
    education_level:     int   = 1     # 1=FP, 2=Grado, 3=Máster, 4=Doctorado
    prev_companies:      int   = 1     # número de empresas anteriores
    has_leadership:      int   = 0     # 0/1
    has_remote_exp:      int   = 0     # 0/1
    certifications:      int   = 0     # número de certificaciones relevantes
    # Añade aquí cualquier feature extra que use tu modelo


class ChatRequest(BaseModel):
    """Proxy simple a Claude (compatibilidad con el HTML en MODE='backend')."""
    system: str
    user:   str


class AnalyzeRequest(BaseModel):
    """
    Pipeline completo híbrido:
      1) Extrae features del texto del candidato
      2) Pasa por el modelo ML → obtiene score
      3) Enriquece el prompt con ese score
      4) Claude genera el informe narrativo
    """
    agent_key:      str             # 'nexus' | 'forma' | 'pulse' | 'aria'
    candidate_name: str
    profile_text:   str
    system_prompt:  str
    # Features opcionales; si no se envían, se intentan inferir del texto
    features:       Optional[PredictRequest] = None


# ── Utilidades ────────────────────────────────────────────────────────────────

FEATURE_ORDER = [
    "years_experience", "skills_match", "education_level",
    "prev_companies", "has_leadership", "has_remote_exp", "certifications"
]

def features_to_array(feat: PredictRequest) -> np.ndarray:
    """Convierte el schema a un array en el orden que espera el modelo."""
    return np.array([[getattr(feat, f) for f in FEATURE_ORDER]], dtype=float)


def infer_features_from_text(text: str) -> PredictRequest:
    """
    Heurística básica para extraer features cuando no se envían explícitamente.
    Personaliza esta función según tu dataset de entrenamiento.
    """
    text_lower = text.lower()

    # Años de experiencia: busca patrones "X años"
    import re
    years = 0.0
    match = re.search(r'(\d+)\s*a[ñn]os?', text_lower)
    if match:
        years = min(float(match.group(1)), 30)

    # Educación
    edu = 2  # Grado por defecto
    if any(w in text_lower for w in ["doctorado", "phd", "doctor"]):
        edu = 4
    elif any(w in text_lower for w in ["máster", "master", "mba", "postgrado"]):
        edu = 3
    elif any(w in text_lower for w in ["fp", "ciclo", "técnico superior"]):
        edu = 1

    # Liderazgo
    leadership = int(any(w in text_lower for w in [
        "lider", "líder", "manager", "jefe", "director", "coordinador", "team lead"
    ]))

    # Experiencia remota
    remote = int(any(w in text_lower for w in ["remoto", "remote", "teletrabajo", "distributed"]))

    # Certificaciones
    certs = len(re.findall(
        r'\b(aws|azure|gcp|pmp|scrum|agile|cissp|cka|ckad|tensorflow|pytorch)\b', text_lower
    ))

    # Empresas previas (aproximado)
    companies = max(1, len(re.findall(r'\b(en|at|@)\s+[A-Z][a-zA-Z]+', text)))

    return PredictRequest(
        years_experience=years,
        skills_match=0.5,           # valor neutro si no se puede calcular
        education_level=edu,
        prev_companies=min(companies, 10),
        has_leadership=leadership,
        has_remote_exp=remote,
        certifications=min(certs, 10),
    )


def score_to_label(score: float) -> str:
    if score >= 0.80: return "Excelente ajuste"
    if score >= 0.60: return "Buen candidato"
    if score >= 0.40: return "Candidato moderado"
    return "Ajuste bajo"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": ml_model is not None}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Ejecuta el modelo ML y devuelve el score de empleabilidad.
    """
    try:
        model = get_model()
        X = features_to_array(req)

        # Score de probabilidad (si el modelo soporta predict_proba)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            score = float(proba.max())
            prediction = int(model.classes_[proba.argmax()])
        else:
            prediction = int(model.predict(X)[0])
            score = float(prediction) / 100.0 if prediction > 1 else float(prediction)

        return {
            "prediction":  prediction,
            "score":       round(score, 3),
            "score_pct":   round(score * 100, 1),
            "label":       score_to_label(score),
            "features_used": req.model_dump(),
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {e}")


@app.post("/chat")
def chat(req: ChatRequest):
    """
    Proxy simple a Claude. Compatible con el HTML cuando MODE='backend'.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY no configurada")
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1000,
            system=req.system,
            messages=[{"role": "user", "content": req.user}]
        )
        return {"text": message.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Pipeline híbrido completo:
      1) Infiere o recibe features del candidato
      2) Obtiene score del modelo ML
      3) Inyecta el score en el prompt como contexto objetivo
      4) Claude genera el informe narrativo enriquecido
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY no configurada")

    # ── Paso 1: Obtener score ML ──────────────────────────────────────────────
    ml_score = None
    ml_label = "No disponible"
    ml_features = {}

    try:
        model = get_model()
        features = req.features or infer_features_from_text(req.profile_text)
        X = features_to_array(features)

        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            raw_score = float(proba.max())
        else:
            raw_score = float(model.predict(X)[0])
            if raw_score > 1:
                raw_score = raw_score / 100.0

        ml_score   = round(raw_score * 100, 1)
        ml_label   = score_to_label(raw_score)
        ml_features = features.model_dump()

    except FileNotFoundError:
        # Si el modelo no está cargado, continuamos sin score ML
        ml_score = None
    except Exception as e:
        ml_score = None

    # ── Paso 2: Enriquecer el prompt con el score ML ──────────────────────────
    ml_context = ""
    if ml_score is not None:
        ml_context = (
            f"\n\n---\n"
            f"📊 **SCORE ML OBJETIVO** (calculado por modelo sklearn/XGBoost):\n"
            f"  • Score de empleabilidad: **{ml_score}/100** — {ml_label}\n"
            f"  • Años de experiencia detectados: {ml_features.get('years_experience', 'N/A')}\n"
            f"  • Nivel educativo: {ml_features.get('education_level', 'N/A')}\n"
            f"  • Liderazgo: {'Sí' if ml_features.get('has_leadership') else 'No'}\n"
            f"  • Exp. remota: {'Sí' if ml_features.get('has_remote_exp') else 'No'}\n"
            f"  • Certificaciones relevantes: {ml_features.get('certifications', 0)}\n"
            f"\nUsa este score como ancla objetiva en tu análisis. "
            f"Si el candidato parece más fuerte o débil narrativamente, explica la diferencia.\n"
            f"---"
        )

    enriched_user_msg = req.profile_text + ml_context

    # ── Paso 3: Llamar a Claude con el prompt enriquecido ─────────────────────
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1200,
            system=req.system_prompt,
            messages=[{"role": "user", "content": enriched_user_msg}]
        )
        claude_response = message.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error llamando a Claude: {e}")

    return {
        "text":        claude_response,
        "ml_score":    ml_score,
        "ml_label":    ml_label,
        "ml_features": ml_features,
        "ml_available": ml_score is not None,
    }
