from fastapi import FastAPI

app = FastAPI(title="QuinotoSpec Example API", version="1.0.0")


@app.get("/")
async def root():
    return {"status": "ok", "message": "QuinotoSpec Example API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
