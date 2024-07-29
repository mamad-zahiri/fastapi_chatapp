import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from src.db.models import Group, GroupChat, GroupMember, PrivateChat, User
from src.settings import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    return db


def get_collection(name: str) -> AsyncIOMotorCollection:
    db = get_db()
    return db.get_collection(name)


async def init_client():
    global client

    client = AsyncIOMotorClient(
        host=settings.db_host,
        port=settings.db_port,
        username=settings.db_username,
        password=settings.db_password,
        maxPoolSize=settings.db_max_connection_count,
        minPoolSize=settings.db_min_connection_count,
        uuidRepresentation=settings.db_uuid_representation,
    )

    # Initialize beanie with the Sample document class and a database
    await init_beanie(
        database=client.db_name,
        document_models=[
            User,
            Group,
            PrivateChat,
            GroupChat,
            GroupMember,
        ],
    )


def init_db():
    global db

    if client is None:
        raise Exception("client is not initialized")

    db = client.get_database(settings.db_name)


def close_connection():
    global client

    if client is None:
        logging.warning("Connection is None, nothing to close.")
        return

    client.close()
    client = None
    logging.info("Mongo connection closed.")
