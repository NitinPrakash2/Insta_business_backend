from fastapi import FastAPI
#set..
from src.shared.util.include_file.index import include_file;
from src.db_config import engine, Base


app = FastAPI(title="FastAPI", version="0.1")



"""
# Create tables if not using Alembic
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""






# 🔐 Add middleware
#app.add_middleware(AuthMiddleware, token="secret-token")
#set..
#app.include_router(router, prefix="/admin") #router


#====party_1====#  [START]
def _party_1(_v={
    "party": str
}):
    _dta = {
        "app": {
        "global": app,
        "this_public": FastAPI(title="FastAPI", version="0.1"),
        "this_private": FastAPI(title="FastAPI", version="0.1"),
        },
        "prefix": "/admin",
        "prefix_public": "/admin-public",
    }
    AuthMiddleware_name, AuthMiddleware_module = include_file(f"src/parties/{_v["party"]}/middlewares/auth.py", lambda name, module: ())[0]
    AuthMiddleware = AuthMiddleware_module.AuthMiddleware 

    #set..
    include_file(f"src/parties/{_v["party"]}/routes",
        lambda name, 
        module: 
           (
            module.index({}) #_dta #print(name, module)
            #,print(module._ins['router']['public'])
            #set..
            #,_dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix=_dta['prefix'])
            #,_dta["app"]["global"].include_router(module._ins['router']['public'], prefix="") # _dta['prefix']

            ,_dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix="")

            ,_dta["app"]["this_private"].include_router(module._ins['router']['private'], prefix="" ) #_dta["prefix"]

            #set..
            #,_dta["app"]["global"].mount(_dta["prefix"], _dta["app"]["this_public"])


            #set..
            ,_dta["app"]["global"].mount(
                _dta["prefix_public"], 
                _dta["app"]["this_public"]
            )


            #set..
            ,_dta["app"]["global"].mount(
                _dta["prefix"], 
                _dta["app"]["this_private"]
            )

            #middleware
            ,_dta["app"]["this_private"].add_middleware(AuthMiddleware)
            
           )
    )
_party_1({
    "party": "party_1"
})
#====party_1====#  [END]





#====party_2====#  [START]
def _party_2(_v={
    "party": str
}):
    _dta = {
        "app": {
        "global": app,
        "this_public": FastAPI(title="FastAPI", version="0.1"),
        "this_private": FastAPI(title="FastAPI", version="0.1"),
        },
        "prefix": "/client",
        "prefix_public": "/client-public",
    }
    AuthMiddleware_name, AuthMiddleware_module = include_file(f"src/parties/{_v["party"]}/middlewares/auth.py", lambda name, module: ())[0]
    AuthMiddleware = AuthMiddleware_module.AuthMiddleware 

    #set..
    include_file(f"src/parties/{_v["party"]}/routes",
        lambda name, 
        module: 
           (
            module.index({}) #_dta #print(name, module)
            #,print(module._ins['router']['public'])
            #set..
            #,_dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix=_dta['prefix'])
            #,_dta["app"]["global"].include_router(module._ins['router']['public'], prefix="" ) # _dta['prefix']

            ,_dta["app"]["this_public"].include_router(module._ins['router']['public'], prefix="")

            ,_dta["app"]["this_private"].include_router(module._ins['router']['private'], prefix="" ) # _dta["prefix"]

            #set..
            #,_dta["app"]["global"].mount(_dta["prefix"], _dta["app"]["this_public"])


            #set..
            ,_dta["app"]["global"].mount(
                _dta["prefix_public"], 
                _dta["app"]["this_public"]
            )


            #set..
            ,_dta["app"]["global"].mount(
                _dta["prefix"], 
                _dta["app"]["this_private"]
            )

            #middleware
            ,_dta["app"]["this_private"].add_middleware(AuthMiddleware)
            
           )
    )
_party_2({
    "party": "party_2"
})
#====party_2====#  [END]





