from typing import Any, Literal, Optional

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
        r = db("Boopt", "Empresas").insert_one(self.model_dump(exclude={"id_"}))
        assert r.acknowledged, "Ocorreu algo de errado. Tente novamente mais tarde."

    def atualizar(self, novos_dados: dict[str, str]) -> None:
        r = db("Boopt", "Empresas").update_one(
            {"_id": self.id_},
            {"$set": {campo: valor for campo, valor in novos_dados.items()}},
        )
        assert r.acknowledged, "Ocorreu algo de errado. Tente novamente mais tarde."

    @classmethod
    def buscar(cls, identificador: Literal["_id", "nome"], valor: str):
        if identificador == "_id":
            valor = ObjectId(valor)
        empresa = db("Boopt", "Empresas").find_one({identificador: valor})
        assert empresa, "Essa empresa não existe."

        return cls(**empresa)
