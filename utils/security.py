from typing import Annotated

from authx import AuthX, AuthXConfig, TokenPayload
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

config = AuthXConfig()
config.JWT_SECRET_KEY = "your-super-secret-key"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=config)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


AccessTokenDepend = Annotated[TokenPayload, Depends(security.access_token_required)]


async def require_admin(payload: AccessTokenDepend) -> TokenPayload:
    if getattr(payload, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required.",
        )
    return payload


AdminDepend = Annotated[TokenPayload, Depends(require_admin)]
