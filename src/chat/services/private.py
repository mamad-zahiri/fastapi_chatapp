from socketio import AsyncServer

from src.chat.services.clients import online_users
from src.db.models import PrivateChat


async def create_private_message_service(private_message: PrivateChat):
    return await private_message.create()


async def send_private_message_service(sio: AsyncServer, private_message: PrivateChat):
    payload = private_message.model_dump()
    sid = online_users.get(private_message.receiver.email)

    if sid is not None:
        await sio.emit(
            "/private/chat",
            data=payload,
            to=sid,
        )

    return payload
