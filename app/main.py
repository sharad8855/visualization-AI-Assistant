from fastapi import FastAPI

app = FastAPI(title="Visualization Project")

@app.get("/")
async def root():
    return {"message": "Welcome to Visualization Project"} 