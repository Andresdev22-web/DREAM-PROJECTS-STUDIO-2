
from pydantic import BaseModel, ConfigDict 
from typing import Literal
class SolicitudCreate(BaseModel):
    correo: str
    nombre_discord: str
    puesto_principal: str

class SolicitudUpdate(BaseModel):
    estado: Literal["PENDIENTE", "ACEPTADO", "RECHAZADO"] = "PENDIENTE"
    fecha_creacion: str 
  