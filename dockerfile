FROM python:3.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1

# 의존성 파일들을 복사
COPY ./pkg/pip_requirements.txt ./pkg/pip_requirements_dev.txt ./

# 의존성 설치
RUN pip install -r pip_requirements_dev.txt

# 애플리케이션 코드 복사
COPY ./src ./src

# FastAPI 앱 실행 (HMR 적용)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]