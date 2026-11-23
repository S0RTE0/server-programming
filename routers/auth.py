import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas.auth import TokenResponse, UserRead, UserRegister
from services.auth import AuthService, get_auth_service
from utils.security import security

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

AuthServiceDepend = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    path="/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserRegister, auth_service: AuthServiceDepend):
    try:
        existing_user = await auth_service.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        return await auth_service.register(data=user_data)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to register user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        ) from exc


@router.post(path="/login", response_model=TokenResponse)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDepend,
):
    try:
        user = await auth_service.authenticate(
            email=credentials.username,
            password=credentials.password,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = security.create_access_token(
            uid=str(user.id),
            data={"role": user.role},
        )
        return TokenResponse(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to authenticate user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user",
        ) from exc
