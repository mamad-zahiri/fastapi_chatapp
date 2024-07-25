from pydantic import EmailStr


class OnlineUsers:
    # TODO: use redis as cache server
    #   It is not a good practice to save online users in dictionary. Instead
    #   we could save them in a Redis Cache or something.
    __online_users: dict[EmailStr, str] = {}

    def all(self) -> dict[EmailStr, str]:
        return self.__online_users

    def get(self, email: EmailStr) -> str:
        return self.__online_users.get(email)

    def add(self, email: EmailStr, sid: str):
        self.__online_users.update({email: sid})

    def pop(self, sid) -> EmailStr:
        for email, _sid in self.all().items():
            if _sid == sid:
                return self.__online_users.pop(email)


online_users = OnlineUsers()
