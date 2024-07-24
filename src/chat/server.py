import socketio

from src.chat.events import sio

sio_app = socketio.ASGIApp(sio)

