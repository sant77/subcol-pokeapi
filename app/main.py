from fastapi import FastAPI
from infrastructure.api.fastapi_controllers import router

app = FastAPI(
    title="Pokemon Counter API",
    version="1.0.0"
)
app.include_router(router, prefix="/v1/counter")
