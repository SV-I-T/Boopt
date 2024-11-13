from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from utils import db


class Missao(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    nome: Optional[str] = None
    descricao: Optional[str] = None
    dti: Optional[datetime] = None
    dtf: Optional[datetime] = None
    participantes: Optional[list[ObjectId]] = []
    campo_desc: Optional[str] = None
    empresa: Optional[ObjectId] = None
    midia: Optional[bool] = False

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True

    def salvar(self) -> None:
        r = db("Missões").update_one(
            {"_id": self.id_ or ObjectId()},
            upsert=True,
            update={"$set": self.model_dump(by_alias=True, exclude_unset=True)},
        )
        assert (
            r.acknowledged
        ), "Ocorreu um erro ao salvar a missão. Tente novamente mais tarde."

    @classmethod
    def consultar_missao(cls, id_missao: str | ObjectId = None):
        missao = db("Missões").find_one({"_id": ObjectId(id_missao)})
        return cls(**missao)
