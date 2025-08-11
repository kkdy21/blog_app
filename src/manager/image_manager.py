import os
import time

from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.datastructures import UploadFile

load_dotenv()


class ImageManager:
    # save image to static/images
    # return image path

    def __init__(self) -> None:
        self.image_upload_path = os.getenv("IMAGE_UPLOAD_PATH") or "./"
        self.default_image_path = f"{self.image_upload_path}/blog_default.png"
        self.volume_path = os.getenv("VOLUME_PATH") or "/usr/src/app"
        if not os.path.exists(self.image_upload_path):
            os.makedirs(self.image_upload_path)

    def save_image(self, author: str, image: UploadFile) -> str:
        """파일 저장을 실제로 담당하는 '동기' 함수"""

        # 고유하고 안전한 파일명 생성
        filename = image.filename or "upload_error.svg"
        filename_only, ext = os.path.splitext(filename)
        upload_filename = f"{filename_only}_{(int)(time.time())}{ext}"

        author_dir = os.path.join(self.image_upload_path, author)
        if not os.path.exists(author_dir):
            os.makedirs(author_dir)

        full_path = os.path.join(author_dir, upload_filename)

        print(f"Saving file (sync) to: {full_path}")
        try:
            with open(full_path, "wb") as outfile:
                while content := image.file.read(1024):
                    outfile.write(content)
                print("upload succeeded:", full_path)
        except Exception as e:
            # 실제 운영 코드에서는 로깅을 하는 것이 좋습니다.
            print(f"File save error: {e}")
            raise HTTPException(
                status_code=500, detail="파일 저장 중 오류가 발생했습니다."
            ) from e

        return full_path.replace(self.volume_path, "")

    # 절대경로로 저장해야하는걸 주의 해야함.
    def resolve_image_url(self, image_url: str | None) -> str:
        if not image_url:
            return self.default_image_path

        return image_url
