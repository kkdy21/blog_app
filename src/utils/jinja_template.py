from typing import Optional

from fastapi.templating import Jinja2Templates


class JinjaSingleton:
    _instance: Optional["JinjaSingleton"] = None
    templates: Jinja2Templates

    def __new__(cls) -> "JinjaSingleton":
        """
        클래스의 새 인스턴스를 생성할 때 호출됩니다.
        인스턴스가 없으면 새로 생성하고, 있으면 기존 인스턴스를 반환합니다.
        """
        if cls._instance is None:
            # 아직 인스턴스가 생성되지 않았을 경우에만 실행됩니다.
            cls._instance = super(JinjaSingleton, cls).__new__(cls)
            # 단 한번만 Jinja2Templates를 초기화합니다.
            cls._instance.templates = Jinja2Templates(directory="src/templates")
        return cls._instance


# 다른 모듈에서 간편하게 사용할 수 있도록 싱글톤 인스턴스를 미리 생성합니다.
jinja_manager = JinjaSingleton()
