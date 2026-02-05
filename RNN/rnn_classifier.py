import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding, SpatialDropout1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

# --- CONFIGURACIÓN ---
CSV_PATH = 'KB_prueba_minima.csv'
GENERATED_SAMPLES_PER_CATEGORY = 300   # Más datos para Deep Learning
MAX_NB_WORDS = 5000     # Máximo número de palabras en el vocabulario
MAX_SEQUENCE_LENGTH = 100 # Longitud fija de los CVs (padding/truncating)
EMBEDDING_DIM = 64      # Dimensión de los vectores de palabras

def cargar_knowledge_base():
    """Carga y estructura las keywords desde el CSV (Igual que antes)."""
    try:
        df = pd.read_csv(CSV_PATH, sep=',')
    except FileNotFoundError:
        print(f"Error: No se encuentra '{CSV_PATH}'")#Capturamos el error
        return {}

    df.columns = df.columns.str.strip()
    kb = {}
    
    if 'Category' not in df.columns:
        print("Error: Columna 'Category' no encontrada.")
        return {}

    for category, grupo in df.groupby('Category'):
        palabras = []
        cols_interes = ['Keywords', 'Skills', 'Tools']
        for col in cols_interes:
            if col in grupo.columns:
                texto_col = ' '.join(grupo[col].dropna().astype(str).tolist())
                texto_limpio = texto_col.replace(',', ' ')
                palabras.extend(texto_limpio.split())
        
        palabras = [p.strip() for p in palabras if len(p.strip()) > 1]
        kb[category] = palabras
    
    return kb
######################################################################################################################################
#--Generamos datos sintétivos
def generar_datos_sinteticos(kb, samples_per_cat=200):
    """Genera datos sintéticos para entrenar la RNN."""
    data = []
    labels = []
    
    print(f"Generando {samples_per_cat * len(kb)} ejemplos sintéticos...")
    for category, keywords in kb.items():
        if len(keywords) < 3: continue
            
        for _ in range(samples_per_cat):
            # Simulamos frases más largas para la RNN
            num_words = random.randint(5, 15) 
            selected_words = random.sample(keywords, min(num_words, len(keywords)))
            # Mezclamos para perder el orden original (simular variedad)
            random.shuffle(selected_words)
            text = " ".join(selected_words)
            data.append(text)
            labels.append(category)
            
    return pd.DataFrame({'text': data, 'label': labels})

def preparar_datos_rnn(df):
    """Tokeniza y prepara secuencias para la LongShortTermemory (RNN)."""
    # 1. Tokenizer
    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, filters=r'!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
    tokenizer.fit_on_texts(df['text'].values)
    word_index = tokenizer.word_index
    print(f'Found {len(word_index)} unique tokens.')

    # 2. Convertir texto a secuencias de números
    X = tokenizer.texts_to_sequences(df['text'].values)
    
    # 3. Padding (hacer que todas tengan la misma longitud)
    X = pad_sequences(X, maxlen=MAX_SEQUENCE_LENGTH)
    
    # 4. One-Hot Encoding de etiquetas
    lb = LabelBinarizer()
    Y = lb.fit_transform(df['label'])
    
    return X, Y, tokenizer, lb
######################################################################################################################################
#--Construimos el modelo
def construir_modelo(input_length, num_classes):
    """Define la arquitectura de la Red Neuronal."""
    model = Sequential()
    # Capa de Embedding: Aprende relaciones semánticas
    model.add(Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=input_length))
    # Dropout espacial para evitar overfitting en embeddings
    model.add(SpatialDropout1D(0.2))
    # Capa LSTM
    model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    # Capa de Salida
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    return model
######################################################################################################################################
#--Entrenamos el modelo
def entrenar_y_evaluar(model, X_train, X_test, Y_train, Y_test):
    """Entrena el modelo y grafica la historia."""
    epochs = 5
    batch_size = 64
    
    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, Y_test), verbose=1)
    
    # Evaluación final
    accr = model.evaluate(X_test, Y_test)
    print(f'Test set\n  Loss: {accr[0]:0.3f}\n  Accuracy: {accr[1]:0.3f}')
    
    # Graficar
    plt.title('Loss')
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='test')
    plt.legend()
    plt.show() # Mostrar gráfico de Loss
    
    plt.title('Accuracy')
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='test')
    plt.legend()
    plt.show() # Mostrar gráfico de Accuracy

import pickle
import os

# ... (Previous code remains) ...

if __name__ == "__main__":
    # 1. Cargar datos
    kb = cargar_knowledge_base()
    if not kb: exit()
    
    # 2. Generar
    df = generar_datos_sinteticos(kb, samples_per_cat=GENERATED_SAMPLES_PER_CATEGORY)
    
    # 3. Prepara (Tokenización y Padding)
    X, Y, tokenizer, lb = preparar_datos_rnn(df)
    
    # 4. Split
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
    
    # 5. Construir
    num_classes = Y.shape[1]
    model = construir_modelo(MAX_SEQUENCE_LENGTH, num_classes)
    
    # 6. Entrenar
    entrenar_y_evaluar(model, X_train, X_test, Y_train, Y_test)

    # 7. GUARDAR EL MODELO PARA SU USO EN LA API
    print("\n--- GUARDANDO ARTEFACTOS DEL MODELO ---")
    model_filename = 'jobnest_rnn_model.keras'
    tokenizer_filename = 'tokenizer.pickle'
    lb_filename = 'label_binarizer.pickle'
    
    model.save(model_filename)
    print(f"Modelo guardado en: {model_filename}")
    
    with open(tokenizer_filename, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Tokenizer guardado en: {tokenizer_filename}")
    
    with open(lb_filename, 'wb') as handle:
        pickle.dump(lb, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Binarizador de etiquetas guardado en: {lb_filename}")
    print("¡Listo para usar en la API!")
