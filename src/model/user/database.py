from dataclasses import dataclass


@dataclass
class UserData:
    id: int
    name: str
    email: str
    is_email_verified: bool


@dataclass
class UserDataPass(UserData):
    hashed_password: str
    created_at: str
