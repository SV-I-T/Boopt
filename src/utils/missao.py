from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Missao(BaseModel):
    nome: str
    fase: Optional[str] = None
    dt_inicio: datetime
    dt_fim: datetime
