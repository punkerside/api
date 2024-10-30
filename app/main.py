from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
import jwt
import requests

# Configuración de FastAPI y CORS
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('titan-prod-api')

# Configuración de AWS Cognito
COGNITO_REGION = "us-east-1"
COGNITO_USERPOOL_ID = "us-east-1_CjoxA2bkB"
COGNITO_JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}/.well-known/jwks.json"

# Cargar las claves públicas de Cognito
jwks = requests.get(COGNITO_JWKS_URL).json()

# Clase de servicio
class Service(BaseModel):
    service_name: str
    status: str
    owner: str
    latest_change: str

# Función para verificar el token JWT
def verify_token(authorization: str = Header(...)):
    token = authorization.split(" ")[1]  # Extrae el token desde "Bearer <token>"

    try:
        # Obtener el encabezado del JWT para extraer el kid
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header")

    # Buscar la clave pública en JWKS que coincida con el kid del encabezado
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break

    if rsa_key:
        try:
            # Convertir la clave pública en un objeto que pyjwt puede usar
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="1ff928076h03393d9a6fqa43ek",  # Reemplaza con tu Client ID de Cognito
                issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=str(e))
    else:
        raise HTTPException(status_code=401, detail="Public key not found for token verification")

# Endpoint para obtener servicios (con verificación JWT)
@app.get("/services", response_model=list[Service], dependencies=[Depends(verify_token)])
async def get_services():
    try:
        response = table.scan()
        items = response.get('Items', [])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clase para crear un nuevo servicio
class NewService(BaseModel):
    service_name: str
    status: str
    owner: str
    latest_change: str

# Endpoint para agregar servicios (con verificación JWT)
@app.post("/services", response_model=NewService, dependencies=[Depends(verify_token)])
async def add_service(service: NewService):
    try:
        table.put_item(Item={
            "service_name": service.service_name,
            "status": service.status,
            "owner": service.owner,
            "latest_change": service.latest_change
        })
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
