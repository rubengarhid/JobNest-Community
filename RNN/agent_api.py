from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import tensorflow as tf
import pickle
import numpy as np
import pdfplumber
import io
from tensorflow.keras.preprocessing.sequence import pad_sequences

# --- CONFIGURACIÓN ---
MODEL_PATH = 'jobnest_rnn_model.keras'
TOKENIZER_PATH = 'tokenizer.pickle'
LB_PATH = 'label_binarizer.pickle'
MAX_SEQUENCE_LENGTH = 100

app = FastAPI(title="JobNest AI Agent", description="API para clasificar CVs usando RNN")

# Variables globales para cargar el modelo en memoria
model = None
tokenizer = None
label_binarizer = None

@app.on_event("startup")
def load_artifacts():
    """Carga el modelo y los tokenizers al iniciar el servidor."""
    global model, tokenizer, label_binarizer
    try:
        print("Cargando modelo...")
        model = tf.keras.models.load_model(MODEL_PATH)
        
        print("Cargando tokenizer...")
        with open(TOKENIZER_PATH, 'rb') as handle:
            tokenizer = pickle.load(handle)
            
        print("Cargando binarizador...")
        with open(LB_PATH, 'rb') as handle:
            label_binarizer = pickle.load(handle)
            
        print("¡Sistema listo para clasificar!")
    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudieron cargar los artefactos. {e}")
        print("Asegúrate de haber ejecutado 'python rnn_classifier.py' primero.")

def extract_text_from_pdf_bytes(file_bytes):
    """Extrae texto de un archivo PDF en memoria."""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
        return text
    except Exception as e:
        return ""

@app.post("/analyze_cv")
async def analyze_cv(file: UploadFile = File(...)):
    """Endpoint principal: Recibe PDF -> Devuelve Predicción."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    # 1. Leer archivo
    contents = await file.read()
    text = extract_text_from_pdf_bytes(contents)
    
    if not text or len(text) < 10:
        return {"error": "No se pudo extraer texto del PDF o está vacío."}
    
    # 2. Preprocesar para la RNN
    # Limpiamos y tokenizamos igual que en el entrenamiento
    seq = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH)
    
    # 3. Predecir
    prediction = model.predict(padded)
    
    # 4. Interpretar resultado
    # Obtenemos el índice con mayor probabilidad
    idx = np.argmax(prediction)
    confidence = float(prediction[0][idx])
    label = label_binarizer.classes_[idx]
    
    # Devolver todas las probabilidades (opcional)
    all_probs = {cls: float(prob) for cls, prob in zip(label_binarizer.classes_, prediction[0])}
    
    return {
        "filename": file.filename,
        "predicted_role": label,
        "confidence": round(confidence * 100, 2),
        "details": all_probs
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
