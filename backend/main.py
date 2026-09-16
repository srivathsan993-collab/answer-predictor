from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import io
import traceback
from predictor import Predictor
from metrics import calculate_metrics

app = FastAPI(title="LLM Science Exam Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8002", "http://127.0.0.1:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = None

class SingleQuestionRequest(BaseModel):
    id: Optional[str] = "1"
    prompt: str
    A: str
    B: str
    C: str
    D: str
    E: str
    answer: Optional[str] = None
@app.on_event("startup")
async def startup_event():
    global predictor
    try:
        predictor = Predictor(model_dir="../../models")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": predictor is not None
    }

@app.post("/predict/single")
async def predict_single(request: SingleQuestionRequest):
    if predictor is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet."})
        
    try:
        data = {
            "id": [request.id],
            "prompt": [request.prompt],
            "A": [request.A],
            "B": [request.B],
            "C": [request.C],
            "D": [request.D],
            "E": [request.E]
        }
        if request.answer:
            data["answer"] = [request.answer]
            
        df = pd.DataFrame(data)
        predictions = predictor.predict(df)
        
        if len(predictions) > 0:
            return predictions[0]
        else:
            return JSONResponse(status_code=500, content={"error": "No prediction generated."})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})

@app.post("/predict")
async def predict_endpoint(file: UploadFile = File(...)):
    if predictor is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet."})
        
    if not file.filename.endswith(".csv"):
        return JSONResponse(status_code=400, content={"error": "Invalid file format. Please upload a CSV file."})
        
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        required_cols = ['id', 'prompt', 'A', 'B', 'C', 'D', 'E']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            return JSONResponse(status_code=400, content={
                "error": f"Invalid CSV.\n\nMissing required columns:\n{', '.join(missing)}\n\nRequired format:\n{','.join(required_cols)}\n\nOptional:\nanswer"
            })
            
        predictions = predictor.predict(df)
        
        response = {
            "total_questions": len(df),
            "predictions": predictions
        }
        
        if 'answer' in df.columns:
            y_true = df['answer'].astype(str).tolist()
            y_pred = [p['top_prediction'] for p in predictions]
            top_3_preds = [p['prediction'] for p in predictions]
            
            # y_prob should be shape (N, 5) with order A,B,C,D,E
            options = ['A', 'B', 'C', 'D', 'E']
            y_prob = []
            for p in predictions:
                probs = [p['probabilities'][opt] for opt in options]
                y_prob.append(probs)
                
            metrics = calculate_metrics(y_true, y_pred, y_prob=y_prob, top_3_preds=top_3_preds)
            response["metrics"] = metrics
            
        return response
        
    except pd.errors.EmptyDataError:
        return JSONResponse(status_code=400, content={"error": "The uploaded CSV file is empty."})
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": f"Internal server error: {str(e)}"})
