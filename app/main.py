from fastapi import FastAPI

app = FastAPI(title="Trading Simulator API")

@app.get("/health")
def health():
    return {"ok": True}