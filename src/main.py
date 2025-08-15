from fastapi import FastAPI

from src.utils.bootstrap import lifespan
from src.utils.middewares import add_middlewares

app = FastAPI(lifespan=lifespan)

add_middlewares(app)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     from time import perf_counter

#     start = perf_counter()
#     response = await call_next(request)
#     duration_ms = (perf_counter() - start) * 1000
#     response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
#     return response
