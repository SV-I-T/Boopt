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
    def buscar_ultimo(cls, id_usr: ObjectId) -> dict | None:
        r = db("AssessmentVendedores", "Aplicações").aggregate(
            [
                {"$unwind": "$participantes"},
                {"$match": {"participantes": id_usr}},
                # Buscar somente a última aplicação para o usuário
                {"$sort": {"_id": -1}},
                {"$limit": 1},
                {
                    "$lookup": {
                        "from": "Respostas",
                        "let": {
                            "id_aplicacao": "$_id",
                            "participantes": "$participantes",
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$id_usuario", "$$participantes"]},
                                            {
                                                "$eq": [
                                                    "$id_aplicacao",
                                                    "$$id_aplicacao",
                                                ]
                                            },
                                        ]
                                    }
                                }
                            },
                            # Buscar somenta a última resposta
                            {"$sort": {"_id": -1}},
                            {"$limit": 1},
                            {
                                "$project": {
                                    "id_aplicacao": 0,
                                    "id_usuario": 0,
                                    "notas": 0,
                                }
                            },
                        ],
                        "as": "resposta",
                    }
                },
                {"$set": {"resposta": {"$first": "$resposta._id"}}},
                {
                    "$project": {
                        "_id": 1,
                        "id_form": 0,
                        "empresa": 0,
                        "participantes": 0,
                    }
                },
            ]
        )
        if r.alive:
            return r.next()
        else:
            return None
