from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AI-Powered Investor Intelligence Platform"
)

# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )