from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 🔧 FastAPI Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧾 Request schema
class PredictRequest(BaseModel):
    data_time: str
    location: str
    county: str

# 🚀 Predict endpoint
@app.post("/predict")
async def predict_endpoint(req: PredictRequest):
    # Simulated risk prediction logic
    # You can replace this later with model inference
    if "Los Angeles" in req.county:
        risk_level = "High"
        lat, lng = 34.0522, -118.2437
    elif "Santa Clara" in req.county:
        risk_level = "Medium"
        lat, lng = 37.3541, -121.9552
    else:
        risk_level = "Low"
        lat, lng = 36.7783, -119.4179

    return {
        "risk_level": risk_level,
        "lat": lat,
        "lng": lng
    }

# 🌐 Root page
@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>🚀 Server running</h1>"

# ⏯️ Optional Local Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
