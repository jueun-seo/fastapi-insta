from fastapi import FastAPI

from routers import auth, posts

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)


@app.get('/')
def home():
  return {'hi': 'hello'}
