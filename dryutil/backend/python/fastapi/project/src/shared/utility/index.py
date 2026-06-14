
from typing import Any
from fastapi import Request, HTTPException, Depends
from src.shared.util.include_file.index import include_file;
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db_config import get_db
from src.database.entity.instance import Instance
from src.database.entity.project import Project
from sqlalchemy.orm import joinedload




async def index(_p={'data':Any}):

    async def i(request:Request, params:dict, db: any):
        #print("--i")
        try:
            #body = await request.json()
            #const { id } = request.params;
            #print(params)
            utility_id = None


            #set..
            project_name = params['project']
            instance_name = params['instance']
            #print(project_name)

            result = await db.execute(
            select(Instance)
            .join(Project, Instance.project_id == Project.id)
            .where(
                Instance.name == instance_name,
                Project.name == project_name,
                #Instance.user_id == request.state.user["id"]  # 👈 restrict to user
            )
            .options(
                joinedload(Instance.project),
                joinedload(Instance.utility),
                )  # optional: eager load
            )
            instance = result.scalar_one_or_none()


            #print(instance)
            
            if not instance:
                raise Exception("invalid id")
            # all ok..
            #update..
            utility_id = f"{instance.utility_id}" #instance.utility_id
            #all done..



 
            #check & set..
            #if "utility_id" in body:
                #utility_id = body['utility_id']; #request.query



            #vali..
            if not utility_id:
                raise Exception("utility_id is not valid")
            #all ok..


            #set..
            lib_name, _lib_ = include_file(f"src/shared/utility/l/{utility_id}/index.py", lambda name, module: ())[0]
            #print(_lib_.index)
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await _lib_.index({
                'data': {
                    'instance': instance
                }
            })
            _lib = await i(request)
            #print(_lib)

            #set..
            _r = _lib
            #all done..


            #set..
            return _r
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Schema validation error: {e.args}")

        
    async def i_init(request:Request):
        return



    #set..
    async def get_schema_for_create(request:Request, params:dict, db: any):
        #print("--get_schema_for_create")
        try:
            #body = await request.json()
            body = await request.json() if await request.body() else {}
            #const { id } = request.params;
            #print(params)
            utility_id = None



            #check & set..
            if "id" in params:
                instance_id = params['id']
                #print(instance_id)

                result = await db.execute(
                    select(Instance).where(Instance.id == instance_id)
                )
                instance = result.scalar_one_or_none()
                #print(instance)
                if not instance:
                    raise Exception("invalid id")
                # all ok..
                #update..
                utility_id = f"{instance.utility_id}" #instance.utility_id
            #all done..


 
            #check & set..
            if "utility_id" in body:
                utility_id = body['utility_id']; #request.query
            


            #check & set..
            if "utility_id" in params:
                utility_id = params['utility_id']; #request.query
            

            #print(body)



            #vali..
            if not utility_id:
                raise Exception("utility_id is not valid")
            #all ok..


            #set..
            lib_name, _lib_ = include_file(f"src/shared/utility/l/{utility_id}/index.py", lambda name, module: ())[0]
            #print(_lib_.index)
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await _lib_.index({
                'data': {
                    #"utility_id": utility_id
                }
            })
            _lib = await get_schema_for_create(request)
            #print(_lib)

            #set..
            _r = _lib
            _r_body = _r['body']
            _r['body'] = {
                    "type": 'object',
                    "required": ['name', 'project_id', 'utility_id', 'config_id', 'data'],
                    "properties": {
                      "name": { "type": 'string', 'minLength': 1 },
                      "project_id": { "type": 'string', "minLength": 1 },
                      "utility_id": { "type": 'string', "minLength": 1 },
                      "config_id": { "type": ['string', 'null'], "minLength": 1 },
                      #set..
                      "data": _r_body['properties']['data'],
                    
                    },
                    "example": {
                      "id": "xxxxx-3ab9-4f72-9f34-aeda3ccdd216",
                      "name": "MY_INSTANCE_NAME",
                      "project_id": "xxxxx-16b6-486c-a7ae-2094ded7caa8",
                      "utility_id": f"{utility_id}",
                      "config_id": None,
                      "data": _r_body['example']['data']
                   }
            }
            #all done..


            #set..
            return _r
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Schema validation error: {e.args}")

    #set..
    async def get_schema_for_run(request:Request, params:dict, db: any):
        #print("--get_schema_for_run")
        try:
            #body = await request.json()
            #const { id } = request.params;
            #print(params)
            utility_id = None


            #set..
            project_name = params['project']
            instance_name = params['instance']
            #print(project_name)

            result = await db.execute(
            select(Instance)
            .join(Project, Instance.project_id == Project.id)
            .where(
                Instance.name == instance_name,
                Project.name == project_name,
                #Instance.user_id == request.state.user["id"]  # 👈 restrict to user
            )
            .options(
                joinedload(Instance.project),
                joinedload(Instance.utility),
                )  # optional: eager load
            )
            instance = result.scalar_one_or_none()


            #print(instance)
            
            if not instance:
                raise Exception("invalid id")
            # all ok..
            #update..
            utility_id = f"{instance.utility_id}" #instance.utility_id
            #all done..



 
            #check & set..
            #if "utility_id" in body:
                #utility_id = body['utility_id']; #request.query



            #vali..
            if not utility_id:
                raise Exception("utility_id is not valid")
            #all ok..


            #set..
            lib_name, _lib_ = include_file(f"src/shared/utility/l/{utility_id}/index.py", lambda name, module: ())[0]
            #print(_lib_.index)
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await _lib_.index({
                'data': {}
            })
            _lib = await get_schema_for_run(request)
            #print(_lib)

            #set..
            _r = _lib
            #all done..


            #set..
            return _r
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Schema validation error: {e.args}")

    #set.. #Sample="http://localhost:8000/client-public/api/doc-ui/project/instance"
    async def get_doc_for_run(request:Request, params:dict, db: any):
        #print("--get_doc_for_run")
        try:
            #body = await request.json()
            #const { id } = request.params;
            #print(params)
            utility_id = None


            #set..
            project_name = params['project']
            instance_name = params['instance']
            #print(project_name)

            result = await db.execute(
            select(Instance)
            .join(Project, Instance.project_id == Project.id)
            .where(
                Instance.name == instance_name,
                Project.name == project_name,
                #Instance.user_id == request.state.user["id"]  # 👈 restrict to user
            )
            .options(
                joinedload(Instance.project),
                joinedload(Instance.utility),  # 👈 eager load related utility
                
                )  # optional: eager load
            )
            instance = result.scalar_one_or_none()


            #print(instance)
            
            if not instance:
                raise Exception("invalid id")
            # all ok..
            #update..
            utility_id = f"{instance.utility_id}" #instance.utility_id
            #all done..



 
            #check & set..
            #if "utility_id" in body:
                #utility_id = body['utility_id']; #request.query



            #vali..
            if not utility_id:
                raise Exception("utility_id is not valid")
            #all ok..


            #set..
            lib_name, _lib_ = include_file(f"src/shared/utility/l/{utility_id}/index.py", lambda name, module: ())[0]
            #print(_lib_.index)
            i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run = await _lib_.index({
                'data': {
                    'instance': instance,
                }
            })
            _lib = await get_doc_for_run(request)
            #print(_lib)

            #set..
            _r = _lib
            #all done..


            #set..
            return _r
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Schema validation error: {e.args}")




    #set..
    return i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run