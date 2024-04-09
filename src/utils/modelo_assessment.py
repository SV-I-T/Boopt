from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from utils.banco_dados import db


def id_form_padrao() -> ObjectId:
    return db("AssessmentVendedores", "Formulários").find_one({}, {"_id": 1})["_id"]


class AssessmentVendedor(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    descricao: str = ""
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

    @classmethod
    def resultado(cls, id_resposta: ObjectId) -> dict | None:
        r = db("AssessmentVendedores", "Respostas").aggregate(
            [
                {"$match": {"_id": ObjectId(id_resposta)}},
                {
                    "$lookup": {
                        "from": "Aplicações",
                        "localField": "id_aplicacao",
                        "foreignField": "_id",
                        "as": "aplicacao",
                    }
                },
                {
                    "$lookup": {
                        "from": "Formulários",
                        "localField": "aplicacao.id_form",
                        "foreignField": "_id",
                        "as": "form",
                    }
                },
                {"$unwind": {"path": "$aplicacao", "preserveNullAndEmptyArrays": True}},
                {"$unwind": {"path": "$form", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "_id": 0,
                        "notas": 1,
                        "form": {
                            "competencias": {
                                "nome": 1,
                                "frases": {"id": 1, "notas": 1},
                            },
                            "etapas": 1,
                        },
                    },
                },
            ]
        )

        if r.alive:
            return r.next()
        else:
            return None

    @classmethod
    def testes_disponiveis(cls, id_usr: ObjectId) -> dict | None:
        r = db("AssessmentVendedores", "Aplicações").aggregate(
            [
                {"$match": {"participantes": id_usr}},
                # # Buscar somente a última aplicação para o usuário
                {"$sort": {"_id": -1}},
                {"$limit": 1},
                {
                    "$lookup": {
                        "from": "Respostas",
                        "let": {"id_aplicacao": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {"$eq": ["$id_usuario", id_usr]},
                                }
                            },
                            {
                                "$project": {
                                    "id_aplicacao": 1,
                                }
                            },
                        ],
                        "as": "respostas",
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "ultima_aplicacao": {
                            "id": "$_id",
                            "resposta": {"$in": ["$_id", "$respostas.id_aplicacao"]},
                        },
                        "ultima_resposta_id": {"$max": "$respostas._id"},
                    }
                },
            ]
        )
        if r.alive:
            return r.next()
        else:
            return None

    @classmethod
    def buscar_respostas(cls, id_usr: ObjectId) -> list[ObjectId]:
        r = db("AssessmentVendedores", "Respostas").find(
            {"id_usuario": id_usr}, {"_id": 1}
        )
        return [i["_id"] for i in r]
