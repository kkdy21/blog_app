import os

from celery import Celery

"""
docker-compose.yml 파일에서 아래 코드를 실행하면, Celery에게 "어디에 있는 설정 정보를 보고 일해야 하는지" 알려주는 부분입니다.
command: celery -A src.worker.celery_app.celery_app worker --loglevel=info

이 파일에는 Celery 애플리케이션의 인스턴스를 생성하고, 주요 설정을 구성하는 코드가 들어가야 합니다. 
이 파일은 Celery 워커가 실행될 때 가장 먼저 참조하는 '설정 파일'이자 '진입점(Entrypoint)'입니다.
"""
broker_url = os.getenv("CELERY_BROKER_URL")
result_backend = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "blog_app",
    broker=broker_url,
    backend=result_backend,
    include=["src.worker.tasks"],
)

celery_app.conf.update(timezone="Asia/Seoul", task_track_started=True)
