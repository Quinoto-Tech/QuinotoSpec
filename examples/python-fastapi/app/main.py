from fastapi import FastAPI

from app.routes import users

app = FastAPI(title="QuinotoSpec Example API", version="1.0.0")
app.include_router(users.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "QuinotoSpec Example API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
