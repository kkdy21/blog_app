from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from passlib.context import CryptContext


class PasswordManager:
    """비밀번호 해싱/검증을 담당하는 관리자 클래스.

    - 기본 알고리즘은 bcrypt
    - deprecated 정책 및 라운드 수를 옵션으로 조정 가능
    - 해싱, 검증, 재해싱 필요 여부 확인 메서드 제공
    """

    def __init__(
        self,
        schemes: Iterable[str] | None = None,
        deprecated: str = "auto",
        bcrypt_rounds: int | None = None,
    ) -> None:
        context_kwargs: dict[str, Any] = {
            "schemes": list(schemes) if schemes else ["bcrypt"],
            "deprecated": deprecated,
        }
        if bcrypt_rounds is not None:
            context_kwargs["bcrypt__rounds"] = bcrypt_rounds

        self._context: CryptContext = CryptContext(**context_kwargs)

    def hash(self, plain_password: str) -> str:
        """평문 비밀번호를 안전하게 해싱합니다."""
        return cast(str, self._context.hash(plain_password))

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """평문 비밀번호가 해시와 일치하는지 검증합니다."""
        return cast(bool, self._context.verify(plain_password, hashed_password))

    def needs_rehash(self, hashed_password: str) -> bool:
        """현재 정책 기준으로 재해싱이 필요한지 확인합니다.
        로그인 등으로 “평문 비밀번호를 받은 순간”에 최신 정책으로 다시 해싱해서 DB에 저장합니다.
        """
        return cast(bool, self._context.needs_update(hashed_password))
