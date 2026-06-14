from sqlalchemy.ext.asyncio import AsyncSession
from app.models.token import RefreshToken
from app.core.security import hash_token
from sqlalchemy import select


async def get_refresh_token_by_jti(jti: str, db: AsyncSession):
    results = await db.execute(select(RefreshToken).where(RefreshToken.id == jti))
    return results


async def revoke_refresh_token(jti: str, db: AsyncSession):
    token = get_refresh_token_by_jti(jti, db)
    if token:
        token.revoked = True  # ty:ignore[unresolved-attribute]
        await db.commit()


async def create_refresh_token_entry(
    user_id: str, token: str, jti: str, expires_at, db: AsyncSession
):
    db_token = RefreshToken(
        id=jti, user_id=user_id, token_hash=hash_token(token), expires_at=expires_at
    )
    db.add(db_token)
    await db.commit()
