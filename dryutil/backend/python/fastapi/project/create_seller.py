import asyncio, os, uuid, json, sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as db:

        # Check if table exists
        r = await db.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='instagram_business')"))
        exists = r.scalar()
        sys.stderr.write(f"instagram_business table exists: {exists}\n")

        if not exists:
            sys.stderr.write("Table not found - engine not initialized yet. Start server first.\n")
            return

        # Check existing row
        r2 = await db.execute(text("SELECT id, user_id FROM instagram_business WHERE user_id='seller_nitin_001'"))
        row = r2.fetchone()
        if row:
            sys.stderr.write(f"Row already exists: id={row[0]}\n")
            return

        # Create row
        new_id = uuid.uuid4()  # UUID object, not string
        data = {
            "config": {
                "database": {"url": DATABASE_URL},
                "meta": {
                    "access_token": "",
                    "instagram_business_account_id": "",
                    "instagram_username": "",
                    "fb_page_id": "",
                    "fb_page_name": "",
                    "catalog_id": ""
                }
            },
            "profile": {"title": "Nitin Store"}
        }
        await db.execute(
            text("INSERT INTO instagram_business (id, user_id, data) VALUES (:id, :uid, CAST(:data AS jsonb))"),
            {"id": new_id, "uid": "seller_nitin_001", "data": json.dumps(data)}
        )
        await db.commit()
        sys.stderr.write(f"Created instagram_business row: id={new_id}\n")

    await engine.dispose()

asyncio.run(main())
