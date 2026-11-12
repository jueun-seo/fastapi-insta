from fastapi import UploadFile, HTTPException
from pathlib import Path
import uuid
from PIL import Image, ImageOps, UnidentifiedImageError

# 사진을 저장할 폴더 (없으면 만들기)
MEDIA_DIR = Path('media')
MEDIA_DIR.mkdir(exist_ok=True)


def save_photo(photo: UploadFile):
    # 1. 업로드된 파일을 이미지로 열기 (사진이 아닌 파일이면 에러 대신 400으로 알려주기)
    try:
        image = Image.open(photo.file)
        image.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail='이미지 파일만 올릴 수 있습니다.')

    # 2. 폰으로 찍은 사진은 옆으로 누워 저장되는 경우가 있어서 바로 세우기
    image = ImageOps.exif_transpose(image)

    # 3. 1080 x 1080 정사각형으로 자르고 줄이기
    image = image.convert('RGB')
    image = ImageOps.fit(image, (1080, 1080))

    # 4. 저장 이름: 겹치지 않는 랜덤 이름. 확장자는 사용자가 보낸 값이 아니라 우리가 정한 .jpg로 고정
    name = f'{uuid.uuid4().hex}.jpg'

    # 5. 줄인 이미지를 jpg로 저장 (JPEG는 투명 배경을 못 써서 RGB로 바꾼 뒤 저장)
    image.convert('RGB').save(MEDIA_DIR / name, 'JPEG', quality=85)

    # 6. DB에 저장할 주소(이름)
    return f'/media/{name}'
