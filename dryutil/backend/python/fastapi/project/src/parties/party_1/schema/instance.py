from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from jsonschema import validate, ValidationError
#set..
from src.shared.util.include_file.index import include_file;
from src.shared.utility.index import index;
from uuid import UUID
from src.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession



"""

# Body JSON Schema
BODY_SCHEMA = {
    "title": "InferenceRequest",
    "type": "object",
    "properties": {
        "text": {"type": "string", "example": "Hello AI"},
        "options": {
            "type": "object",
            "properties": {"reverse": {"type": "boolean", "default": True}},
        },
    },
    "required": ["text"]
}

# Query JSON Schema (for documentation / reference)
QUERY_SCHEMA = {
    "title": "QueryParams",
    "type": "object",
    "properties": {
        "verbose": {"type": "boolean", "default": False}
    }
}

# Path JSON Schema
PATH_SCHEMA = {
    "title": "PathParams",
    "type": "object",
    "properties": {
        "version": {"type": "string", "pattern": "^v[0-9]+$"}
    },
    "required": ["version"]
}

"""



#set..
async def body(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        #validate(instance=data, schema=BODY_SCHEMA)  # validate against your JSON schema
        i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await index({'data':{}})
        _SCHEMA = await get_schema_for_create(request, {}, db)
        _BODY_SCHEMA = _SCHEMA['body']
        #print(_SCHEMA)
        validate(instance=data, schema=_BODY_SCHEMA)  # validate against your JSON schema

        return data
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Schema validation error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e}")
    


#set..
async def patch_body(request: Request, id: str, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        #validate(instance=data, schema=BODY_SCHEMA)  # validate against your JSON schema
        i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await index({'data':{}})
        _SCHEMA = await get_schema_for_create(request,{
            "id": id
        }, db)
        _BODY_SCHEMA = _SCHEMA['body']
        #print(_SCHEMA)

        #update..
        _BODY_SCHEMA['required'] = []
        print(_BODY_SCHEMA)

        validate(instance=data, schema=_BODY_SCHEMA)  # validate against your JSON schema

        print('--vali')

        return data
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Schema validation error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {e}")
    


