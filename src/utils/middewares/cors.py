from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:8000",
    # "*",
    "null",
]


def add_cors_middleware(app: FastAPI) -> None:
    print("add_cors_middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
