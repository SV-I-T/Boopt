from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from utils.banco_dados import db


def id_form_padrao() -> ObjectId:
    return db("AssessmentVendedores", "Formulários").find_one({}, {"_id": 1})["_id"]


class AssessmentVendedor(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    id_form: Optional[ObjectId] = Field(default_factory=id_form_padrao)
    empresa: ObjectId
    participantes: list[ObjectId] = Field(default_factory=list)

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True

    def registrar(self) -> None:
        r = db("AssessmentVendedores", "Aplicações").insert_one(
            self.model_dump(exclude={"id_"})
        )
        assert r.acknowledged, "Ocorreu algo de errado. Tente novamente mais tarde."
