from fastapi import APIRouter, Body, Query, Path, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse
#from my_ai_project.services.model import predict
#from src.parties.party_1.schema.instance import body
from src.parties.party_1.controllers.instance import index as controller_index
#set..
from src.shared.util.include_file.index import include_file;
from src.db_config import get_db
from uuid import UUID
import uuid



#set..
_ins = {
    "router": {
       "public": APIRouter(),
       "private": APIRouter(), #APIRouter(dependencies=[Depends(AuthMiddleware)]),
    }
}



#set..
def index(_p={}):



    #set..
    router = _ins["router"]["public"]
    router_private = _ins["router"]["private"]

    #set..
    _ep_prefix_0 = "/api/instance"
    #set..
    _ep_prefix_2 = "/api/doc";
    _ep_prefix_3 = "/api/doc-ui";


    
    #set..
    @router.post(_ep_prefix_0+'/test-public')
    async def run(
        #version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
        #body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
        #verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
    ):
        #return controller_index()[0]()
        #create = controller_index()  # get inner functions
        #_rsp = create;
        #return  _rsp;
        _func, _ = await controller_index()   # unpack functions
        return await _func()       # call create
    


    

    #============PRIVATE==========# [START]
    #set..
    @router_private.post(_ep_prefix_0+'/create')
    async def run(
        request: Request,
        #version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
        #body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
        body: dict = Depends( include_file("src/parties/party_1/schema/instance.py", lambda name, module: ())[0][1].body ),
        #verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
        db=Depends(get_db)
    ):

        #return controller_index()[0]()
        #create = controller_index()  # get inner functions
        #_rsp = create;
        #return  _rsp;
        _func, _, _, _, _ = await controller_index()   # unpack functions
        return await _func(request,body,db)       # call create
    



    #set..
    @router_private.put(_ep_prefix_0+'/update/'+"{id}")
    async def run(
        request: Request,
        id: UUID,
        #version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
        #body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
        body: dict = Depends( include_file("src/parties/party_1/schema/instance.py", lambda name, module: ())[0][1].body ),
        #verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
        db=Depends(get_db)
    ):

        #return controller_index()[0]()
        #create = controller_index()  # get inner functions
        #_rsp = create;
        #return  _rsp;
        _, _, _func, _, _ = await controller_index()   # unpack functions
        return await _func(request,id,body,db)       # call create
    


    #set..
    @router_private.patch(_ep_prefix_0+'/patch/'+"{id}")
    async def run(
        request: Request,
        id: UUID,
        #version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
        #body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
        body: dict = Depends( include_file("src/parties/party_1/schema/instance.py", lambda name, module: ())[0][1].patch_body ),
        #verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
        db=Depends(get_db)
    ):

        #return controller_index()[0]()
        #create = controller_index()  # get inner functions
        #_rsp = create;
        #return  _rsp;
        _, _, _, _func, _ = await controller_index()   # unpack functions
        return await _func(request,id,body,db)       # call create
    


    
    #set.. "Sample" = "http://localhost:8000/admin-public/api/doc-ui/utility:9"
    @router_private.get(_ep_prefix_2+'/utility:'+"{utility}", include_in_schema=False)
    async def run(
        request: Request,
        utility: str,
        #version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
        #body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
        #body: dict = Depends( include_file("src/parties/party_1/schema/instance.py", lambda name, module: ())[0][1].body ),
        #verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
        db=Depends(get_db)
    ):

        #return controller_index()[0]()
        #create = controller_index()  # get inner functions
        #_rsp = create;
        #return  _rsp;

        #set vars..
        body = None
        project = None
        instance = None

        _, _, _, _, _func = await controller_index()   # unpack functions
        #return await _func(request,body,db)       # call create
        return await _func(request,utility,db)
    
        """
        return JSONResponse(
                content={"status": "success", "output": {"id": "-"}},
                status_code=201,
        )
        """
    

    #============PRIVATE==========# [END]






    #============PUBLIC==========# [START]
    @router.get(_ep_prefix_3+'/utility:'+"{utility}", include_in_schema=False)
    async def swagger_ui():
      #print("--swagger_ui")
      _dta = {
          "suffix": uuid.uuid4(),
      }
      html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Dynamic Swagger Docs</title>
      <link rel="stylesheet" type="text/css"
            href="https://unpkg.com/swagger-ui-dist/swagger-ui.css" />
    </head>
    <body>
      <div id="swagger-ui"></div>
      <div id="form-ui-{_dta['suffix']}" >
        <div > Access token </div>
        <div style="height:1vh;" > </div>
        <input id="a-token-ui-{_dta['suffix']}" type="text" placeholder="paste your access-token.." />
        <div style="height:1vh;" > </div>
        <button id="update-ui-{_dta['suffix']}" >Update</button>
        <div style="height:1vh;" > </div>
        <div > <b>NOTE:</b> Access token is required to view Api Docs </div>
      </div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>
        let _d = {{
          "access_token": localStorage.getItem('access_token'),
          "u_arr": location.pathname.split('/')
        }};
        let _u = {{
          "a_arr": _d['u_arr'][4].split(':')
        }};
        //alert(JSON.stringify(_dta))
        console.log(_d.u_arr);
        let mE_f = document.getElementById("form-ui-{_dta['suffix']}");
        let mE_a = document.getElementById("a-token-ui-{_dta['suffix']}");
        let mE_b = document.getElementById("update-ui-{_dta['suffix']}");
        //set..
        mE_b.onclick = () => {{
        const _v = mE_a.value.trim();
        //console.log(_v);
        localStorage.setItem('access_token', _v);
        //refresh..
        location.href = location.href;
        }};
        //check & set..
        if (_d[`access_token`]){{
        /*SwaggerUIBundle({{
          url: `/client/api/doc/${{_d['u_arr'][4]}}/${{_d['u_arr'][5]}}`, //'/client/api/doc/ona/vibe_coding', //'/swagger.json',
          dom_id: '#swagger-ui',
          presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        }});
        */

        fetch(`/admin/api/doc/${{_d['u_arr'][4]}}`, {{
  headers: {{
    "Authorization": `Bearer ${{_d[`access_token`]}}`,
  }},
}})
  .then(res => res.json())
  .then(spec => {{
    SwaggerUIBundle({{
      spec,  // use the loaded spec directly
      dom_id: "#swagger-ui",
      deepLinking: true,
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
      ],
      layout: "BaseLayout",
      persistAuthorization: true,
      requestInterceptor: (req) => {{
        req.headers["Authorization"] = `Bearer ${{_d[`access_token`]}}`;
        return req;
      }}
    }});
  }})
  .catch(err => {{
    console.error("Failed to load Swagger spec:", err);
    document.body.innerHTML = "<p>❌ Unauthorized or failed to load swagger.json</p>";
  }});

        }}else{{
        //mE_f.style.display = "block";
        }}

      </script>
    </body>
    </html>
    """
      return HTMLResponse(html)

    #============PUBLIC==========# [END]


    













     
    

    














