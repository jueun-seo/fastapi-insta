from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import auth, posts, users

app = FastAPI()

# /media 주소로 media 폴더의 사진을 브라우저가 가져갈 수 있게 열어 두기
app.mount('/media', StaticFiles(directory='media'), name='media')

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)

@app.get('/')
def home():
  return {'hi': 'hello'}
