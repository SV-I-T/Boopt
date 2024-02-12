from bson import ObjectId
from pydantic import BaseModel


class Empresa(BaseModel):
    nome: str
    segmento: str
    gestor_id: list[ObjectId]
