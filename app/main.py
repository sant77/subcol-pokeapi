from fastapi import FastAPI
from infrastructure.api.fastapi_controllers import router

app = FastAPI()
app.include_router(router)
