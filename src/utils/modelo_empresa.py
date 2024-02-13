from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator
from utils.banco_dados import db


class Empresa(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    nome: str
    segmento: Optional[str] = None
    gestores: Optional[list[ObjectId]] = None

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True

    @field_validator("nome", mode="before")
    @classmethod
    def em_branco(cls, v: Any, field) -> Any:
        assert bool(v), "Todos os campos marcados com (*) são obrigatórios"
        return v

    def registrar(self) -> None:
        assert not db("Boopt", "Empresas").find_one(
            {"nome": self.nome}
        ), "Já existe uma empresa come esse nome."
        r = db("Boopt", "Empresas").insert_one(self.model_dump())
        assert r.acknowledged, "Ocorreu algo de errado. Tente novamente mais tarde."
