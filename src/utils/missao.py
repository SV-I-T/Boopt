from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel


class Missao(BaseModel):
    descricao: str
    fase: Optional[str]
    dti: datetime
    dtf: datetime
    empresa: ObjectId
    participantes: list[ObjectId]
    campo_obs: Optional[str]
