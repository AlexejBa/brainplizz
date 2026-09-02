
from fastapi import FastAPI
from app.routers import auth
app = FastAPI(title="BrainPlizz")

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "BrainPlizz server is running!"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BrainPlizz"
    }