# 🚀 JobNest AI Agent - Clasificador de CVs con RNN

Este proyecto utiliza una **Red Neuronal Recurrente (RNN)** con capas **LSTM** para clasificar automáticamente currículums en PDF según categorías profesionales (Data Science, Ciberseguridad, Desarrollo Web, etc.).

## Tecnologías utilizadas
* **Backend:** FastAPI & Uvicorn
* **IA/ML:** TensorFlow, Keras, Scikit-learn
* **Data:** Pandas, Numpy
* **PDF Scraping:** pdfplumber

##  Requisitos necesarios
Instala las dependencias necesarias:
`pip install -r requirements.txt`

## Cómo usar estos archivos:
1. **Entrenamiento:** Ejecuta `python scripts/rnn_classifier.py` para generar el modelo.
2. **Servidor:** Ejecuta `python agent_api.py` para iniciar la API.
3. **Ejecución** Sube el CV y obtén la predicción con tu RNN entrenada previamente.

