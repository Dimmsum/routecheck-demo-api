from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
from routers import items, users, orders, auth

app = FastAPI(title="RouteCheck Demo API", version="1.0.0")

_PG_CODE_TO_STATUS = {
    "23503": (422, "Referenced resource does not exist"),
    "23505": (409, "A record with that value already exists"),
    "23502": (422, "A required field is missing"),
    "22P02": (422, "Invalid input format"),
}


@app.exception_handler(APIError)
async def postgrest_error_handler(request: Request, exc: APIError):
    status, default_msg = _PG_CODE_TO_STATUS.get(exc.code, (500, "Database error"))
    return JSONResponse(status_code=status, content={"detail": exc.message or default_msg})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred"})


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(orders.router)


@app.get("/health")
def health():
    return {"status": "ok"}
