from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.usuarios.api.router import router as usuarios_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(usuarios_router)
