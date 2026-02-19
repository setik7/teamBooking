from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth

from app.database import get_db
from app.config import get_settings
from app.db.models import User
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

oauth = OAuth()

# Register Google
if settings.google_client_id:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# Register GitHub
if settings.github_client_id:
    oauth.register(
        name="github",
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )


async def find_or_create_user(
    db: AsyncSession, email: str, name: str, avatar: str | None, provider: str, oauth_id: str
) -> User:
    result = await db.execute(
        select(User).where(User.oauth_provider == provider, User.oauth_id == oauth_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Check if email exists with different provider
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            # Link to existing account
            user.oauth_provider = provider
            user.oauth_id = oauth_id
        else:
            user = User(
                email=email, name=name, avatar=avatar,
                oauth_provider=provider, oauth_id=oauth_id,
            )
            db.add(user)

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/login/dev")
async def login_dev(request: Request, db: AsyncSession = Depends(get_db)):
    """Dev-only login bypass. Creates/finds a dev user and issues a token directly."""
    user = await find_or_create_user(db, "dev@test.com", "Dev User", None, "dev", "dev1")
    access_token = create_access_token({"sub": str(user.id)})
    return RedirectResponse(f"{settings.frontend_url}/auth/callback?token={access_token}")


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    if provider not in ("google", "github"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=400, detail=f"{provider} OAuth not configured")

    redirect_uri = f"{settings.backend_url}/auth/callback/{provider}"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}")
async def callback(provider: str, request: Request, db: AsyncSession = Depends(get_db)):
    if provider not in ("google", "github"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=400, detail=f"{provider} OAuth not configured")

    token = await client.authorize_access_token(request)

    if provider == "google":
        userinfo = token.get("userinfo", {})
        email = userinfo.get("email")
        name = userinfo.get("name", email)
        avatar = userinfo.get("picture")
        oauth_id = userinfo.get("sub")
    else:  # github
        resp = await client.get("user", token=token)
        profile = resp.json()
        oauth_id = str(profile["id"])
        name = profile.get("name") or profile["login"]
        avatar = profile.get("avatar_url")
        # Get email from GitHub
        email_resp = await client.get("user/emails", token=token)
        emails = email_resp.json()
        primary = next((e for e in emails if e.get("primary")), emails[0] if emails else None)
        email = primary["email"] if primary else f"{profile['login']}@github.noemail"

    user = await find_or_create_user(db, email, name, avatar, provider, oauth_id)
    access_token = create_access_token({"sub": str(user.id)})

    return RedirectResponse(f"{settings.frontend_url}/auth/callback?token={access_token}")


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
async def logout():
    # JWT is stateless; client should discard token
    return {"message": "Logged out"}
