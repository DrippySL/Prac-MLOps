import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from prometheus_client import Counter, Histogram, make_asgi_app

app = FastAPI(
    title="HuggingFace MLOps Inference Service",
    description="Микросервис инференса NLP-модели",
    version="1.0.0"
)

# Инициализация модели Hugging Face с использованием библиотек из готового venv
try:
    classifier = pipeline(
        "text-classification", 
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
except Exception as e:
    classifier = None

class TextRequest(BaseModel):
    text: str

@app.get("/health", summary="Проверка состояния сервиса")
def health_check():
    if classifier is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    return {"status": "healthy"}

@app.post("/predict")
def predict(payload: TextRequest):
    start_time = time.time()
    endpoint = "/predict"
    
    if classifier is None:
        REQUEST_COUNT.labels(endpoint=endpoint, status="503").inc()
        raise HTTPException(status_code=503, detail="Model unavailable")

    try:
        res = classifier(payload.text)[0]
        duration = time.time() - start_time
        
        LATENCY_HISTOGRAM.labels(endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
        
        return {"text": payload.text, "label": res["label"], "score": round(float(res["score"]), 4)}
    except Exception as e:
        REQUEST_COUNT.labels(endpoint=endpoint, status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))