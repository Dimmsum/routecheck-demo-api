from fastapi import FastAPI
from routers import items, users, orders

app = FastAPI(title="RouteCheck Demo API", version="1.0.0")

app.include_router(users.router)
app.include_router(items.router)
app.include_router(orders.router)


@app.get("/health")
def health():
    return {"status": "ok"}
