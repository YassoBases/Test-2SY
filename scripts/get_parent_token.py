"""Print JWT for parent user 23 (browser automation)."""
import asyncio
import logging
import sys
from pathlib import Path

# Keep stdout clean — only the JWT is printed (for execSync piping).
logging.disable(logging.CRITICAL)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import select

from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.models.auth_session import AuthSession
from app.models.user import User  # noqa: F401 — register mappers


async def main() -> None:
    async with AsyncSessionLocal() as db:
        sess = await db.scalar(
            select(AuthSession)
            .where(AuthSession.user_id == 23, AuthSession.revoked_at.is_(None))
            .order_by(AuthSession.created_at.desc())
        )
    print(create_access_token({"sub": "23", "role": "parent"}, session_id=sess.id if sess else None))


if __name__ == "__main__":
    asyncio.run(main())
