import asyncio

from src.database.database import db
from src.database.repositories.auth.refresh_token_repository import RefreshTokensRepository


async def clean_refresh_tokens():
    await RefreshTokensRepository(db=db).delete_all()

if __name__ == "__main__":
    try:
        asyncio.run(clean_refresh_tokens())
    except KeyboardInterrupt:
        print("\nScript interrupted gracefully")