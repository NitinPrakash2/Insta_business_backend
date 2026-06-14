from fastapi import APIRouter, Body, Query, Path
from fastapi.responses import JSONResponse
#from my_ai_project.services.model import predict
from src.parties.party_1.schema.instance import BODY_SCHEMA, QUERY_SCHEMA, PATH_SCHEMA

from src.parties.party_1.controllers.instance import index as controller_index;

router = APIRouter()

_ep_prefix_0 = "/api/instance"

@router.post("{_ep_prefix_0}/{version}")
async def run_inference(
    version: str = Path(..., regex=PATH_SCHEMA["properties"]["version"]["pattern"], description="API version"),
    body: dict = Body(..., embed=False, schema_extra=BODY_SCHEMA),
    verbose: bool = Query(QUERY_SCHEMA["properties"]["verbose"]["default"], description="Verbose output")
):
    """
    Fully validates:
    - Path param `version` (regex from PATH_SCHEMA)
    - Query param `verbose` (from QUERY_SCHEMA)
    - Body JSON (from BODY_SCHEMA)
    """
    """
    text = body.get("text")
    options = body.get("options", {})
    result = predict(text)

    if options.get("reverse", True):
        result = result[::-1]

    if verbose:
        result = f"[v{version}] {result}"
    """
    result = []

    return JSONResponse(content={"output": result})



#set..
@router.post(_ep_prefix_0+'/create')
async def create(
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
