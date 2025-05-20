from fastapi import FastAPI
from .api.routes import router

app = FastAPI(title="Visualization Project")

@app.get("/")
async def root():
    return {"message": "Welcome to Visualization Project"}

app.include_router(router, prefix="/api/v1") 