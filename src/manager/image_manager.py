import os
import time

from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.datastructures import UploadFile

load_dotenv()


class ImageManager:
    def __init__(self) -> None:
        # Docker 환경에서는 컨테이너 내의 절대 경로를, 로컬에서는 상대 경로를 사용합니다.
        # docker-compose.yml에 정의된 환경 변수가 있으면 그 값을 사용하고, 없으면 로컬 환경을 위한 기본값을 사용합니다.
        docker_image_path = os.getenv("IMAGE_UPLOAD_PATH")
        self.image_upload_path = docker_image_path or "src/static/images"
        self.default_image_path = f"{self.image_upload_path}/blog_default.png"
        self.volume_path = os.getenv("VOLUME_PATH") or ""

        if not os.path.exists(self.image_upload_path):
            os.makedirs(self.image_upload_path)

    def save_image(self, author: str, image: UploadFile) -> str:
        """파일 저장을 실제로 담당하는 '동기' 함수"""
        filename = image.filename or "upload_error.svg"
        filename_only, ext = os.path.splitext(filename)
        upload_filename = f"{filename_only}_{(int)(time.time())}{ext}"
        author_dir = os.path.join(self.image_upload_path, author)
        if not os.path.exists(author_dir):
            os.makedirs(author_dir)

        full_path = os.path.join(author_dir, upload_filename)

        try:
            with open(full_path, "wb") as outfile:
                while content := image.file.read(1024):
                    outfile.write(content)
                print("upload succeeded:", full_path)
        except Exception as e:
            print(f"File save error: {e}")
            raise HTTPException(
                status_code=500, detail="파일 저장 중 오류가 발생했습니다."
            ) from e

        return self.trim_volume_path(full_path)

    # 절대경로로 저장해야하는걸 주의 해야함.
    def resolve_image_url(self, image_url: str | None) -> str:
        if not image_url:
            return self.trim_volume_path(self.default_image_path)

        return self.trim_volume_path(image_url)

    def trim_volume_path(self, image_url: str) -> str:
        """
        전체 파일 경로에서 웹 URL로 사용하기 위해 볼륨 경로(prefix)를 제거합니다.
        - Docker: '/usr/src/app/src/static/...' -> '/src/static/...'
        - Local: 'src/static/...' -> 'src/static/...' (변경 없음)
        """
        if self.volume_path and image_url.startswith(self.volume_path):
            # replace를 한 번만 수행하여 경로에 동일한 문자열이 있을 경우의 오류 방지
            return image_url.replace(self.volume_path, "", 1)
        return image_url
