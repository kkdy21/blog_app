from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from src.router import blog
from src.utils import error_handler
from src.utils.bootstrap import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(blog.router)

app.add_exception_handler(HTTPException, error_handler.custom_http_exception_handler)
app.add_exception_handler(
    RequestValidationError, error_handler.custom_validation_exception_handler
)
