import asyncio, os, json, sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as db:
        
        # Update instance with database URL
        data = {
            "config": {
                "database": {"url": DATABASE_URL},
                "meta_app_id": os.getenv("META_APP_ID", ""),
                "meta_app_secret": os.getenv("META_APP_SECRET", ""),
                "oauth_redirect_uri": "http://localhost:5173/oauth/callback"
            }
        }
        
        await db.execute(
            text("UPDATE instance SET data = CAST(:data AS jsonb) WHERE name='instagram' AND project_id IN (SELECT id FROM project WHERE name='ona')"),
            {"data": json.dumps(data)}
        )
        await db.commit()
        sys.stderr.write("Instance updated with database configuration\n")

    await engine.dispose()

asyncio.run(main())
