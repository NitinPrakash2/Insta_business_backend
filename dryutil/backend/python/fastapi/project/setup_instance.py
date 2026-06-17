import asyncio, os, uuid, json, sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with AsyncSession(engine) as db:
        
        # Get or create a user
        r = await db.execute(text("SELECT id FROM \"user\" LIMIT 1"))
        user = r.fetchone()
        if not user:
            user_id = str(uuid.uuid4())
            await db.execute(
                text("INSERT INTO \"user\" (id, email) VALUES (:id, :email)"),
                {"id": user_id, "email": "admin@instagram.local"}
            )
            sys.stderr.write(f"Created user: id={user_id}\n")
        else:
            user_id = user[0]
            sys.stderr.write(f"Using existing user: id={user_id}\n")
        
        # Get or create project 'ona'
        r = await db.execute(text("SELECT id FROM project WHERE name='ona'"))
        project = r.fetchone()
        if not project:
            project_id = str(uuid.uuid4())
            await db.execute(
                text("INSERT INTO project (id, name) VALUES (:id, :name)"),
                {"id": project_id, "name": "ona"}
            )
            sys.stderr.write(f"Created project 'ona': id={project_id}\n")
        else:
            project_id = project[0]
            sys.stderr.write(f"Project 'ona' exists: id={project_id}\n")
        
        # Get or create utility 'instagram' (id=705)
        r = await db.execute(text("SELECT id FROM utility WHERE id='705'"))
        utility = r.fetchone()
        if not utility:
            await db.execute(
                text("INSERT INTO utility (id, name) VALUES (:id, :name)"),
                {"id": "705", "name": "instagram"}
            )
            sys.stderr.write(f"Created utility 'instagram': id=705\n")
            utility_id = "705"
        else:
            utility_id = utility[0]
            sys.stderr.write(f"Utility exists: id={utility_id}\n")
        
        # Check if instance exists
        r = await db.execute(
            text("SELECT id FROM instance WHERE name='instagram' AND project_id=:pid"),
            {"pid": project_id}
        )
        instance = r.fetchone()
        if not instance:
            instance_id = str(uuid.uuid4())
            data = {
                "config": {
                    "meta_app_id": os.getenv("META_APP_ID", ""),
                    "meta_app_secret": os.getenv("META_APP_SECRET", ""),
                    "oauth_redirect_uri": "http://localhost:5173/oauth/callback"
                }
            }
            await db.execute(
                text("INSERT INTO instance (id, user_id, name, project_id, utility_id, data) VALUES (:id, :uid_col, :name, :pid, :uid, CAST(:data AS jsonb))"),
                {"id": instance_id, "uid_col": user_id, "name": "instagram", "pid": project_id, "uid": utility_id, "data": json.dumps(data)}
            )
            sys.stderr.write(f"Created instance 'instagram': id={instance_id}\n")
        else:
            sys.stderr.write(f"Instance 'instagram' already exists: id={instance[0]}\n")
        
        await db.commit()
        sys.stderr.write("Setup complete!\n")

    await engine.dispose()

asyncio.run(main())
