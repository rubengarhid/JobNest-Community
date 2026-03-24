import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security, APIRouter
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

load_dotenv()

app = FastAPI()

API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise RuntimeError("API_KEY not defined")


api_key_header = APIKeyHeader(name='x-api-key')

def get_api_key(api_key = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail='Forbidden')
    return api_key

protected_router = APIRouter(dependencies=[Security(get_api_key)])

@protected_router.get("/name")
def get_name():
    return {"name": "Brivio"}

@protected_router.get('/health')
def health():
    return "Service is healthy."

# TODO: restrict CORS settings
app.add_middleware(CORSMiddleware,
                   allow_origins=['*'], 
                   allow_methods=['*'],
                   allow_headers=['*'],
                   )

app.include_router(protected_router)

handler = Mangum(app)
