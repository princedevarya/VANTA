from fastapi import FastAPI

app = FastAPI(
    title="VANTA",
    description="Evidence-Driven Penetration Testing Platform",
    version="0.1.0",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "project": "VANTA",
        "version": "0.1.0",
    }
