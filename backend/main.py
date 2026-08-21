from fastapi import FastAPI

from .database import Base, engine
from .routes import incidents

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DRISHTI Backend")

app.include_router(incidents.router)


@app.get("/")
def home():
    return {"message": "DRISHTI Backend is running"}