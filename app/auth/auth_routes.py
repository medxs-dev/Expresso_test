from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import text
from app.core.db import get_db
from app.common.utils.auth_utils import create_access_token, verify_password, verify_token_in_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from datetime import datetime, timedelta
router = APIRouter(prefix="/api/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Step 1: Raw SQL to fetch the user
    query = text("""
        SELECT * FROM exp_expresso_users_login
        WHERE email = :username
    """)
    result = await db.execute(query, {"username": form_data.username})
    data = result.fetchone()
    user = dict(data._mapping)
    print("--------------------------------")
    print("Tess:T:::", user)
    print("--------------------------------")

    # Step 2: Validate user and password
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    expired_at = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Step 3: Generate JWT token
    access_token = create_access_token(
        {"sub": user["email"], "role": user["role"]}, expired_at)

    insert_query = text("""
        INSERT INTO expresso_session_login (user_id, access_token, expired_at)
        VALUES (:user_id, :access_token, :expired_at)
    """)

    await db.execute(insert_query, {
        "user_id": user["id"],
        "access_token": access_token,
        "expired_at": datetime.utcnow() + expired_at
    })

    await db.commit()

    return {"access_token": access_token, "token_type": "bearer", "status": "Successfully !!!"}


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),  # ✅ Reuse the same instance
    db: AsyncSession = Depends(get_db)
):

    try:
        # optional, but ensures token is valid+active
        await verify_token_in_db(token, db)
    except HTTPException:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You may allow logout even for expired/invalid tokens"
        )

    query = text("""
        UPDATE expresso_session_login
        SET is_active = FALSE
        WHERE access_token = :token
    """)
    await db.execute(query, {"token": token})
    await db.commit()

    return {"status": "Logout successful"}
