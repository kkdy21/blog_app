# SQLAlchemy의 모든 ORM 모델이 상속받아야 하는 기본 클래스를 정의합니다.
# 이 Base 클래스를 상속받는 모든 클래스는 자동으로 SQLAlchemy에 의해 테이블과 매핑됩니다.
from sqlalchemy.orm import declarative_base

# declarative_base 함수는 ORM 모델의 기본 클래스로 사용할 수 있는 새로운 클래스를 생성합니다.
Base = declarative_base()
