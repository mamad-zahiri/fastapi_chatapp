from pydantic import EmailStr
from redis import Redis

from src.settings import settings

redis = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


class OnlineUsers:
    __redis_hash_set = "online_users"

    def all(self) -> dict[EmailStr, str]:
        return redis.hgetall(self.__redis_hash_set)

    def get(self, email: EmailStr) -> str:
        return redis.hget(self.__redis_hash_set, email)

    def add(self, email: EmailStr, sid: str):
        redis.hset(self.__redis_hash_set, email, sid)

    def pop(self, email: EmailStr) -> EmailStr:
        sid = redis.hget(self.__redis_hash_set, email)
        redis.hdel(self.__redis_hash_set, email)
        return sid


online_users = OnlineUsers()
