from fastapi import FastAPI

app = FastAPI()


@app.get("/")
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "check-in-system"}
