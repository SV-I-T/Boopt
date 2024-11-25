import json
from typing import Optional

from pydantic import BaseModel


class Passo(BaseModel):
    id: int
    desc: str
    peso: int
    comprou: Optional[bool] = None


class Etapa(BaseModel):
    id: int
    nome: str
    sigla: str
    passos: list[Passo]


class RaioX(BaseModel):
    etapas: list[Etapa]
    id_comprou: Optional[int] = None

    @classmethod
    def ler_etapas(cls, v: int = 1):
        with open("./utils/raiox_form.json", "r", encoding="utf8") as f:
            forms = json.load(f)
        form = forms.get(str(v), None)
        if not form:
            return None
        etapas = cls(**form)
        return etapas
