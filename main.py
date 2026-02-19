from fastapi import FastAPI
from app.routes import students, cheating_events, notifications

app = FastAPI(title="Exam Monitoring System", version="1.0.0")

app.include_router(students.router)
app.include_router(cheating_events.router)
app.include_router(notifications.router)

@app.get("/")
def root():
    return {"message": "Exam Monitoring System API", "version": "1.0.0"}