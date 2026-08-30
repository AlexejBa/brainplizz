from fastapi import FastAPI

app = FastAPI(title="BrainPlizz")


@app.get("/")
def root():
    return {"message": "BrainPlizz server is running!"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BrainPlizz"
    }