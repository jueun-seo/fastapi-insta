from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy import select, func

from deps import templates, SessionDep, CurrentUserDep
from models import User, Post, Follow
from photos import save_photo

router = APIRouter()

@router.get('/users/{username}')
def user_profile(
    request: Request,
    username: str,
    db: SessionDep,
    user: CurrentUserDep,
):
    # 주소의 username에 해당하는 프로필 주인 찾기
    owner = db.scalar(select(User).where(User.username == username))
    if owner is None:
        raise HTTPException(status_code=404, detail='해당 사용자가 없습니다.')

    # 프로필 주인이 쓴 글만 최신순으로
    posts = db.scalars(
        select(Post).where(Post.user_id == owner.id).order_by(Post.created_at.desc())
    ).all()

    # 팔로워 수: 프로필 주인을 팔로우하는 사람 (following_id가 주인인 줄)
    follower_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.following_id == owner.id)
    )
    # 팔로잉 수: 프로필 주인이 팔로우하는 사람 (follower_id가 주인인 줄)
    following_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.follower_id == owner.id)
    )

    # 내가 이 프로필 주인을 이미 팔로우했는지 (버튼 모양에 사용)
    is_following = False
    if user:
        is_following = db.get(Follow, (owner.id, user.id)) is not None

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'user': user,    # 지금 로그인한 사람 (nav에서 사용)
            'owner': owner,  # 프로필 주인
            'posts': posts,  # 프로필 주인의 글
            'follower_count': follower_count,
            'following_count': following_count,
            'is_following': is_following,
        }
    )

@router.post('/users/{username}/follows')
def user_follow(
    username: str,
    db: SessionDep,
    user: CurrentUserDep,
):
    # 로그인 안 한 사람
    if user is None:
        return RedirectResponse('/login', status_code=303)

    # 팔로우 당할 사람(프로필 주인) 찾기
    owner = db.scalar(select(User).where(User.username == username))
    if owner is None:
        raise HTTPException(status_code=404, detail='해당 사용자가 없습니다.')

    # 자기 자신은 팔로우 불가
    if owner.id == user.id:
        raise HTTPException(status_code=400, detail='자기 자신은 팔로우할 수 없습니다.')

    # 이미 팔로우했는지 확인 (번호표 순서: following_id, follower_id)
    follow = db.get(Follow, (owner.id, user.id))

    if follow:
        # 이미 팔로우 중 -> 언팔로우
        db.delete(follow)
    else:
        # 아직 안 했음 -> 팔로우
        follow = Follow(follower_id=user.id, following_id=owner.id)
        db.add(follow)

    db.commit()

    return RedirectResponse(f'/users/{username}', status_code=303)


@router.post('/users/{username}/avatar')
def user_avatar(
    username: str,
    db: SessionDep,
    user: CurrentUserDep,
    photo: UploadFile = File()
):
    avatar_url = save_photo(photo)
    user.avatar_url = avatar_url
    db.commit()

    return RedirectResponse(f'/users/{username}', status_code=303)