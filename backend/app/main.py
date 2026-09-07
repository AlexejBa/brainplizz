from fastapi import FastAPI

from app.routers import auth, rooms, questions, game_answer, websocket


app = FastAPI()


app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(questions.router)
app.include_router(game_answer.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    return {"message": "BrainPlizz server is running!"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BrainPlizz"
    }