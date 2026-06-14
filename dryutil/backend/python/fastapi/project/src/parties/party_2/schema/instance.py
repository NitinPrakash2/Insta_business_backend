from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from jsonschema import validate, ValidationError
#set..
from src.shared.util.include_file.index import include_file;
from src.shared.utility.index import index;
from uuid import UUID
from src.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession


 

#set..
async def body(request: Request, project: str, instance: str, db: AsyncSession = Depends(get_db)):
    try:
        #print(project)
        #print(instance)
        #data = await request.json() 
        data = await request.json() if request.headers.get("content-type") == "application/json" else {}
        _query = dict(request.query_params) if request.headers.get("content-type") == "application/json" else {}


        #validate(instance=data, schema=BODY_SCHEMA)  # validate against your JSON schema
        i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await index({'data':{}})


        _SCHEMA = await get_schema_for_run(request,{
            "project": project,
            "instance": instance,
        }, db)
        _BODY_SCHEMA = _SCHEMA['body']
        _QUERY_SCHEMA = _SCHEMA['querystring']
        #print(_SCHEMA)
        #print(_query)


        validate(instance=data, schema=_BODY_SCHEMA)  # validate against your JSON schema

        validate(instance=_query, schema=_QUERY_SCHEMA)  # validate against your JSON schema




        return data
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Schema validation error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e}")
    


