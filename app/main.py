from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

from app.routers import users
from app.autogen import init_data

app = FastAPI()
add_pagination(app)

# Include routers
app.include_router(users.router)


@app.get("/")
async def ping_and_init():
    """Ping endpoint to check if the service is running"""
    init_data()
    return {"Hello": "World"}


@app.exception_handler(ValueError)
async def value_exception_handler(request: Request, exc: ValueError):
    """
    Handles ValueError exceptions
    :param request: Request
    :param exc: ValueError
    """
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles all uncaught exceptions
    :param request: Request
    :param exc: Exception
    """
    return JSONResponse(status_code=500, content={"detail": str(exc)})
