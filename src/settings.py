from decouple import config
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = config("app_name", "Chat Room")

    # JWT
    jwt_access_secret_key: str = config("jwt_access_secret_key")
    jwt_refresh_secret_key: str = config("jwt_refresh_secret_key")
    jwt_access_token_expire: int = config(
        "jwt_access_token_expire",
        default=1800,  # 30 minutes
        cast=int,
    )
    jwt_refresh_token_expire: int = config(
        "jwt_refresh_token_expire",
        default=25200,  # 1 week
        cast=int,
    )
    jwt_algorithm: str = config("jwt_algorithm", default="HS256")

    # MongoDB
    db_name: str = config("db_name", default="my_db")
    db_host: str = config("db_host", default="localhost")
    db_port: int = config("db_port", default=27017, cast=int)
    db_username: str = config("db_username")
    db_password: str = config("db_password")
    db_max_connection_count: int = config("db_max_connection_count", default=10, cast=int)
    db_min_connection_count: int = config("db_max_connection_count", default=3, cast=int)
    db_uuid_representation: str = config("db_uuid_representation", default="standard")


settings = Settings()
