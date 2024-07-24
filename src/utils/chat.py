from typing import Any


def token_provided(auth: dict[str, Any] | None) -> bool:
    if auth is None:
        return False

    if auth.get("token") is None:
        return False

    return True
