from fastapi import FastAPI

from src.router import blog

app = FastAPI()

app.include_router(blog.router)
