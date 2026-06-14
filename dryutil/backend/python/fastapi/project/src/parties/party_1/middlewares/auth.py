from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.shared.util.jwt_handler.index import JWTHandler



class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
           #print("--AuthMiddleware [party_1]")
           request.state.user = None
        
           #set..
           auth_header = request.headers.get("Authorization")
           if auth_header and auth_header.startswith("Bearer "):
               token = auth_header.split(" ")[1]
               try:
                   #raise Exception("test err")
                   # allow expired configurable
                   payload = JWTHandler.decode_token(token, allow_expired=True)

                   #vali..
                   _party = "party_1"
                   if _party not in payload['security']['party']:
                       raise ValueError(f"{_party} not found! Security error")
                   #all ok..


                   #set..
                   request.state.user = {"id": payload.get("sub"), "name": payload.get("name", "Unknown")}

                   #log..
                   #print(payload)
                   #print(request.state.user)

               except Exception as e:
                   raise Exception("Invalid token")

           #vali..
           if not request.state.user:
               raise Exception("Unable to Authenticate!")
           #all ok..

        except Exception as e:
            return JSONResponse({"error": "Invalid token","data":{"log":e.args}}, status_code=401)
        #all ok..


        #set..
        return await call_next(request)