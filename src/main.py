from fastapi import FastAPI

from src.router import blog

app = FastAPI()

app.include_router(blog.router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
