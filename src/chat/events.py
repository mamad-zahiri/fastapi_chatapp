import socketio
from socketio.exceptions import ConnectionRefusedError

from src.auth.services import verify_token_service
from src.utils.chat import token_provided

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")


@sio.on("connect")
async def connect(sid, e, auth):
    if not token_provided(auth):
        raise ConnectionRefusedError()

    if not verify_token_service(auth["token"]):
        raise ConnectionRefusedError()

    await sio.emit("/auth/verify", "verified", to=sid)


@sio.on("disconnect")
async def disconnect(sid):
    await sio.emit("broadcast", data=f"user {sid} disconnected")
