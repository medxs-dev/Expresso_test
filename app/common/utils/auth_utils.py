from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.db import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

ENDPOINT_ACCESS_RULES = {
    "/admin/": ["SUPER_ADMIN", "ADMIN"],
    "/store/": ["SUPER_ADMIN", "ADMIN", "STORE", "DELIVERY"],
    "/cust/": ["SUPER_ADMIN", "ADMIN", "STORE", "DELIVERY", "CUSTOMER"],
    "/v1/store-owners/": ["SUPER_ADMIN", "ADMIN", "DELIVERY"]
}

# Hash password


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Generate JWT token


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Verify token exists in DB and is valid


async def verify_token_in_db(token: str, db: AsyncSession) -> None:
    query = text("""
        SELECT id FROM expresso_session_login
        WHERE access_token = :token
            AND is_active = TRUE
            AND expired_at > (NOW() AT TIME ZONE 'UTC')
        ORDER BY id DESC
        LIMIT 1
    """)

    result = await db.execute(query, {"token": token})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid or expired"
        )

# Verify JWT token, return user info


async def verify_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        await verify_token_in_db(token, db)

        return {"username": username, "role": role}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Role-based access restriction


async def restrict_users_for(
    request: Request,
    user: dict = Depends(verify_token)
) -> dict:
    path = request.url.path

    for endpoint, roles in ENDPOINT_ACCESS_RULES.items():
        if path == endpoint or path.startswith(endpoint.rstrip("/") + "/"):
            if user["role"] in roles:
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized for this path"
                )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )
