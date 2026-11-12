from fastapi import UploadFile
from pathlib import Path
import uuid
import shutil

# 사진을 저장할 폴더 (없으면 만들기)
MEDIA_DIR = Path('media')
MEDIA_DIR.mkdir(exist_ok=True)


def save_photo(photo: UploadFile):
    # 원래 확장자(.jpg 등)만 가져오고, 이름은 겹치지 않게 랜덤으로
    ext = Path(photo.filename).suffix
    name = f'{uuid.uuid4().hex}{ext}'

    # 사진은 글자가 아니라서 'wb'(바이너리 쓰기)
    with open(MEDIA_DIR / name, 'wb') as f:
        shutil.copyfileobj(photo.file, f)

    return f'/media/{name}'
