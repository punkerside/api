from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from boto3.dynamodb.conditions import Key
import os

# Configuración de la aplicación FastAPI
app = FastAPI()

# Configuración de DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('titan-prod-api')

# Modelo de respuesta para el servicio existente
class Service(BaseModel):
    service_name: str
    status: str
    owner: str
    latest_change: str

@app.get("/services", response_model=list[Service])
async def get_services():
    try:
        response = table.scan()  # Escanea todos los registros en la tabla
        items = response.get('Items', [])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Modelo de entrada para agregar un nuevo servicio
class NewService(BaseModel):
    service_name: str
    status: str
    owner: str
    latest_change: str

@app.post("/services", response_model=NewService)
async def add_service(service: NewService):
    try:
        # Insertar un nuevo servicio en la tabla DynamoDB
        table.put_item(Item={
            "service_name": service.service_name,
            "status": service.status,
            "owner": service.owner,
            "latest_change": service.latest_change
        })
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
