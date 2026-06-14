from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Request
from sqlalchemy import update as sqlalchemy_update
from src.db_config import get_db  # your db session dependency
from src.database.entity.instance import Instance  # SQLAlchemy model
import uuid
from src.shared.utility.index import index as utility_index;



#set..
async def index():
    async def create(request: Request, body: dict, db: AsyncSession):
        try:
            user_id = request.state.user["id"]
            new_instance = Instance(
                id=uuid.uuid4(),
                user_id=user_id,
                project_id=body["project_id"],
                utility_id=int(body["utility_id"]),
                config_id=body.get("config_id"),
                name=body["name"],
                description=body.get("description"),
                data=body.get("data"),
            )
            db.add(new_instance)
            await db.commit()
            await db.refresh(new_instance)

            return JSONResponse(
                content={"status": "success", "output": {"id": str(new_instance.id)}},
                status_code=201,
            )
        except Exception as e:
            await db.rollback()
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=400,
            )

    async def get(db: AsyncSession):
        result = await db.execute(select(Instance))
        instances = result.scalars().all()
        return JSONResponse(content={"output": [str(i.id) for i in instances]})

    async def update(request: Request, instance_id: uuid.UUID, body: dict, db: AsyncSession):
        try:
            user_id = request.state.user["id"]
            #print(user_id)

            result = await db.execute(select(Instance).where(
                Instance.id == instance_id,
                Instance.user_id == user_id
            ))
            instance = result.scalar_one_or_none()
            if not instance:
                return JSONResponse(
                    content={"status": "error", "message": "Instance not found"},
                    status_code=404,
                )

            # full replacement (PUT) — overwrite fields
            #instance.user_id = body["user_id"]
            #instance.project_id = body["project_id"]
            #instance.utility_id = int(body["utility_id"])
            instance.config_id = body.get("config_id")
            instance.name = body["name"]
            instance.description = body.get("description")
            instance.data = body.get("data")

            await db.commit()
            await db.refresh(instance)

            return JSONResponse(
                content={"status": "success", "output": {"id": str(instance.id)}},
                status_code=200,
            )
        except Exception as e:
            await db.rollback()
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=400,
            )

    async def patch(request: Request, instance_id: uuid.UUID, body: dict, db: AsyncSession):
        try:
            user_id = request.state.user["id"]
            result = await db.execute(select(Instance).where(
                Instance.id == instance_id,
                Instance.user_id == user_id
            ))
            instance = result.scalar_one_or_none()
            if not instance:
                return JSONResponse(
                    content={"status": "error", "message": "Instance not found"},
                    status_code=404,
                )

            # partial update — only apply fields provided
            for field in [
                #"user_id", "project_id", "utility_id", "config_id", "description", "data"
                "name"
              ]:
                if field in body:
                    value = int(body[field]) if field == "utility_id" else body[field]
                    setattr(instance, field, value)

            await db.commit()
            await db.refresh(instance)

            return JSONResponse(
                content={"status": "success", "output": {"id": str(instance.id)}},
                status_code=200,
            )
        except Exception as e:
            await db.rollback()
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=400,
            )
    
    async def get_doc(request: Request, utility_id: str, db: AsyncSession):
        try:
            #print(f"--get_doc {utility_id}")
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await utility_index({'data':{}})
            _rsp = await get_schema_for_create(request,{
              #"project": project,
              #"instance": instance,
              "utility_id": f"{utility_id}",
            }, db)

            #set vars..
            _create_rsp = _rsp
            _update_rsp = _rsp

            #remove `id` from example..
            try:
              _create_rsp['body']['example'].pop('id', None) 
              #print(_test)
            except:
               pass;


            #set..
            _api_doc = {
        "openapi": "3.0.3",
        "info": {
            "title": f"[Instance] api-docs", 
            "description": f"Utility-id={utility_id}",
            "version": "1.0.0"
        },
        "paths": {
            f"/admin/api/instance/create": {
                "post": {
                    "summary": "Create instance",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/create_instance"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/create_instance"}
                                }
                            }
                        }
                    }
                }
            },
            
            f"/admin/api/instance/update/{{id}}": {
                "put": {
                    "summary": "Update instance",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "Instance ID"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/update_instance"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/update_instance"}
                                }
                            }
                        }
                    }
                }
            },
             
        },
        "components": {
            "schemas": {
            "create_instance": _create_rsp['body'],
            "update_instance": _update_rsp['body'],
            
          
            } 
          },
            }


            return _api_doc #_rsp
        except Exception as e:
            return JSONResponse(
                    content={"status": "error", "message": f"Instance not found [i] {e.args}" },
                    status_code=404,
            )
        

    return create, get, update, patch, get_doc

