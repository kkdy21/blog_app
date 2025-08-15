from dataclasses import dataclass


@dataclass
class UserData:
    id: int
    name: str
    email: str


@dataclass
class UserDataPass(UserData):
    hashed_password: str
    created_at: str
