from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.auth.apis import router as auth_router
from src.chat.server import sio_app as chat_server
from src.db.connection import close_connection, init_client, init_db

app = FastAPI()

app.add_event_handler("startup", init_client)
app.add_event_handler("startup", init_db)
app.add_event_handler("shutdown", close_connection)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth")

app.mount("/static", StaticFiles(directory="public"), name="static")
app.mount("/app", StaticFiles(directory="public", html=True), name="static")

app.mount("/", chat_server)
