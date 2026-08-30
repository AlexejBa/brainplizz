from fastapi import FastAPI

app = FastAPI(title="BrainPlizz")


@app.get("/")
def root():
    return {"message": "BrainPlizz server is running!"}