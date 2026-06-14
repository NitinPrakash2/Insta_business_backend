
from typing import Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
#import requests
import httpx
from src.shared.utility.u.fake_req_obj.index import fake_req_obj


# sample
async def index(_p={'data':{
    'instance': Any,
}}):
    async def i(request:Request):
        try:
            body = await request.json()
            prompt, model = body['prompt'], body['model']


            #set vars..
            _data = _p['data']['instance'].data
            _config = _data['config']
            _instance = _data['instance']
           
            #log..
            #print(prompt)


            #set vars..
            _dta = {
                'var': {
                }
            }
            _ins = {
                'var': {
                }
            }
            

            #set..
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            _r_headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": _config['gemini']['api_key'],
            }
            _r_payload = {
                "contents": [
                    {
                        "parts": [
                            { "text": prompt } #req.prompt
                        ]
                    }
                ]
            }

            #response = await requests.post(url, headers=_r_headers, json=payload)
            #set..
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=_r_headers, json=_r_payload)

            if response.status_code != 200:
                raise Exception(f"status_code={response.status_code}, detail={response.text}")
            #all ok..
            

            #set..
            data = response.json()



            """
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            """



            


            #set..
            return JSONResponse(
                content={"success": True, "data": {
                    "data": data
                }},
                status_code=200,
            )
        except Exception as e:
            return JSONResponse(
                    content={
                       "status": False, 
                       "message": f"Err [i]", 
                       "data": {
                          "log": e.args
                       }
                    },
                    status_code=404,
            )
    
    #set..
    async def i_init(request:Request):
        return
    



    #set..
    async def get_schema_for_create(request:Request):
        return {
            'body': {
                "type": 'object',
                "required": ["data"],
                "properties": {
                  #data: { type: 'object' },
                  "data": { 
                    "type": 'object',
                    "required": ["config","instance"],
                    "properties": {
                        "config": { 
                           "type": 'object',
                           "required": ["gemini"],
                           "properties": {
                             "gemini": { 
                                "type": 'object',
                                "required": ["api_key",],
                                "properties": {
                                    "api_key": { "type": 'string' },

                                }
                            }
                           }

                        },
                        "instance": { 
                           "type": 'object',
                           "required": ["var",],
                           "properties": {
                                "var": { 
                                    "type": 'object',
                                    "required": [
                                        #/*"mysql",*/
                                        ],
                                    "properties": {
                                        #/*mysql: {
                                           #type: 'object',
                                           #required: ["query",],
                                           #properties: {
                                             #query: { type: "string" }
                                           #}
                                        #}*/
                                    }
                                },
                           }
                        },
                    }

                  },
                   
                },
                "example": {
                    "data": {
                        "config": {
                            "gemini": {
                                "api_key": ""
                            }
                        },
                        "instance": {
                            "var": {}
                        }
                    }
                }


            },
            'querystring': {

            }
        }
    

    #set..
    async def get_schema_for_run(request:Request):
        #print("--get_schema_for_run")
        query = dict(request.query_params)
        #print(query['typ'])
        class _sch:
            async def _body(_a={
                'query':dict
            }):
                _n = None

                #set..
                match _a['query']['typ']:
                  case 'prompt':
                      _n = {
                        "type": 'object',
                        "required": ["prompt","model"],
                        "properties": {
                          #data: { type: 'object' },
                          "prompt": { "type": 'string', "minLength": 1 },
                          "model": { 
                            "type": 'string', 
                            "minLength": 1,
                            "enum": ["gemini-2.0-flash",],
                          },
                        }
                      }
                  case 'model':
                      _n = {
                        "type": 'object',
                        "required": ["prompt","model"],
                        "properties": {
                          #data: { type: 'object' },
                          "prompt": { "type": 'string', "minLength": 1 },
                          "model": { 
                            "type": 'string', 
                            "minLength": 1,
                            "enum": ["gemini-2.0-flash",],
                          },
                        }
                      }
                   
                  case _:
                      #return "Default"
                      raise Exception(f"no body schema found..for [typ={_a['query']['typ']}]")
                #all ok..

                 
                #set..
                return _n
        return {
              "body": await _sch._body({
                 'query': query
              }),
              "querystring": {
                "type": 'object',
                "required": ["typ",],
                "properties": {
                  "typ": { 
                    "type": 'string', 
                    "enum": [
                        "prompt",
                        "model",
                    ]
                  },
                }
              }
        };

    #set..
    async def get_doc_for_run(request:Request):
        #body = await request.json()
        #query = dict(request.query_params)
        #print(_p['data']['instance'].project.name)
        #print(_p['data']['instance'].utility.name)
        _var = {
            "ep_name": f"client/api/i/{_p['data']['instance'].project.name}/{_p['data']['instance'].utility.name}", 
        }

        #set..
        return {
        "openapi": "3.0.3",
        "info": {
            "title": f"[i, i_init] api-docs", 
            "description": f"Project={_p['data']['instance'].project.name}, Instance={_p['data']['instance'].name}, Utility={_p['data']['instance'].utility.name}, Utility-id={_p['data']['instance'].utility.id}",
            "version": "1.0.0"
        },
        "paths": {
            f"/{_var['ep_name']}?typ=prompt": {
                "post": {
                    "summary": "prompt",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/prompt"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/prompt"}
                                }
                            }
                        }
                    }
                }
            },
            f"/{_var['ep_name']}?typ=model": {
                "post": {
                    "summary": "model",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/model"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/model"}
                                }
                            }
                        }
                    }
                }
            },
        },
        "components": {
            "schemas": {
            "prompt": (await get_schema_for_run(fake_req_obj(
                method="POST",
                url="",
                headers={}, #{"x-api-key": "abc123"},
                query_params={"typ": "prompt"},
                path_params={}, #{"item_id": 42},
                json_data={}, #{"name": "T-shirt", "price": 19.99},
                state={}, #{"user": "Alice"}
            )))['body'],
            "model": (await get_schema_for_run(fake_req_obj(
                method="POST",
                url="",
                headers={}, #{"x-api-key": "abc123"},
                query_params={"typ": "model"},
                path_params={}, #{"item_id": 42},
                json_data={}, #{"name": "T-shirt", "price": 19.99},
                state={}, #{"user": "Alice"}
            )))['body'],
          
            } 
          },
        }




    #set..
    return i, get_schema_for_create, get_schema_for_run, i_init, get_doc_for_run