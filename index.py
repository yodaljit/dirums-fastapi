from fastapi import FastAPI, HTTPException, Depends, Request, status
from pydantic import BaseModel
from routes.index import products
from fastapi import Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from oauth import get_current_user
from jwttoken import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from config.index import conn
from controllers.otp import get_otp, verify_otp
from jose import jwt, JWTError

from schemas.index import SerailizerDict

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
origins = [
    "https://dirums-fastapi.vercel.app",
    "https://dirums-final.vercel.app",
    "http://65.0.124.105"
]
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Enable TrustedHost middleware to validate the host header
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "dirums-fastapi.vercel.app", "dirums-final.vercel.app", "65.0.124.105"])

# Define a custom middleware to protect certain routes
# @app.middleware("http")
# async def validate_jwt_token(request, call_next):
#     # Check if the request path starts with "/protected"
#     if request.url.path.startswith("/vendors"):
#         # Get the JWT token from the "Authorization" header
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             # Return a 401 Unauthorized response if the JWT token is not provided
#             return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
#         try:
#             # Decode and verify the JWT token with the secret key
#             token = auth_header.split(" ")[1]
#             payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#             # Attach the user ID from the JWT token to the request state
#             request.state.username = payload["sub"]
#         except (JWTError, KeyError):
#             # Return a 401 Unauthorized response if the JWT token is invalid or missing
#             return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
#     # Call the next middleware or route handler if the request is allowed
#     response = await call_next(request)
#     return response

@app.post('/get-login-otp')
def getOTP(phone):
    user = conn.dirums.vendor.find_one({"phone_number": phone})
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return get_otp(user)


@app.post('/verify-otp')
def verifyOTP(phone, otp):
    user = conn.dirums.vendor.find_one({"phone_number": phone})
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    isValid = verify_otp(otp, user)

    if isValid[0]:
        access_token = create_access_token(data={"sub": user["phone_number"]})
        return {"access_token": access_token, "token_type": "bearer", 'user': SerailizerDict(user), 'message': 'OTP verified'}
    else:
        return isValid
    
    


app.include_router(products)
