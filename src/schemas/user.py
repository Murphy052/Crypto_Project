from dataclasses import dataclass


@dataclass
class User:
    username: str
    password: str
    user_id: int | None = None
