from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="FF Codex API", version="0.1.0")

# Include authentication router
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "FF Codex API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
