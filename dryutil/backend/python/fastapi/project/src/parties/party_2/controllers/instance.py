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
     
    async def i(request: Request, project: str, instance: str, body: dict, db: AsyncSession):
        try:
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await utility_index({'data':{}})
            _rsp = await i(request,{
              "project": project,
              "instance": instance,
            }, db)
            return _rsp
        except Exception as e:
            return JSONResponse(
                    content={"status": "error", "message": f"Instance not found [i] {e.args}" },
                    status_code=404,
            )
            
   
    
    async def i_init():
        return
    

    async def get_doc_for_run(request: Request, project: str, instance: str, body: dict, db: AsyncSession):
        try:
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await utility_index({'data':{}})
            _rsp = await get_doc_for_run(request,{
              "project": project,
              "instance": instance,
            }, db)
            return _rsp
        except Exception as e:
            return JSONResponse(
                    content={"status": "error", "message": f"Instance not found [i] {e.args}" },
                    status_code=404,
            )
        
        
          
 
    return i, i_init, get_doc_for_run
