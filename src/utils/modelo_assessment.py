from typing import Any, Literal, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, computed_field
from utils.banco_dados import db


class AssessmentVendedor(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    id_form: Optional[ObjectId] = Field(
        default=db("AssessmentVendedores", "Formulários").find_one({}, {"_id:1"})["_id"]
    )
    empresa: ObjectId
    participantes: list[ObjectId] = Field(default_factory=list)

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True
