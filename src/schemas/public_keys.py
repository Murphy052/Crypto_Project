from dataclasses import dataclass


@dataclass
class PublicKeys:
    public_key_exp: int
    public_key_n: str
    user_id: int
    key_id: int | None = None


@dataclass
class PublicKeySchema:
    public_key_exp: int
    public_key_n: str
