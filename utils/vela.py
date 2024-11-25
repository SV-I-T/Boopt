import pickle
from typing import Optional

import polars as pl
from bson import ObjectId
from pydantic import BaseModel, Field

from utils.banco_dados import db


class VelaAssessmentDataFrames(BaseModel):
    competencias: pl.DataFrame
    etapas: pl.DataFrame

    class Config:
        arbitrary_types_allowed = True


class Vela(BaseModel):
    id_: Optional[ObjectId] = Field(alias="_id", default=None)
    descricao: Optional[str] = None
    v_form: Optional[int] = 1
    empresa: Optional[ObjectId] = None
    participantes: Optional[list[ObjectId]] = []

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True

    def salvar(self) -> None:
        r = db("VelaAplicações").update_one(
            {"_id": self.id_ or ObjectId()},
            upsert=True,
            update={"$set": self.model_dump(by_alias=True, exclude_unset=True)},
        )
        assert r.acknowledged, "Ocorreu algo de errado ao salvar a aplicação Vela. Tente novamente mais tarde."

    @classmethod
    def consultar_aplicacao(cls, id_aplicacao: str | ObjectId = None):
        aplicacao = db("VelaAplicações").find_one({"_id": ObjectId(id_aplicacao)})
        if not aplicacao:
            return None
        return cls(**aplicacao)

    @classmethod
    def resultado(cls, id_resposta: ObjectId) -> dict | None:
        r = db("VelaRespostas").aggregate(
            [
                {"$match": {"_id": id_resposta}},
                {
                    "$lookup": {
                        "from": "VelaAplicações",
                        "localField": "id_aplicacao",
                        "foreignField": "_id",
                        "as": "aplicacao",
                    }
                },
                {
                    "$lookup": {
                        "from": "VelaFormulários",
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
        r = db("VelaAplicações").aggregate(
            [
                {"$match": {"participantes": id_usr}},
                # # Buscar somente a última aplicação para o usuário
                {"$sort": {"_id": -1}},
                {"$limit": 1},
                {
                    "$lookup": {
                        "from": "VelaRespostas",
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
        r = db("VelaRespostas").find({"id_usuario": id_usr}, {"_id": 1})
        return [i["_id"] for i in r]

    @classmethod
    def buscar_aplicacoes(cls, id_empresa: ObjectId):
        r = db("VelaAplicações")

    @classmethod
    def carregar_formulario(cls, v_form: int = 1) -> VelaAssessmentDataFrames:
        with open("./utils/vela_form.pickle", "rb") as f:
            dfs = VelaAssessmentDataFrames(**pickle.load(f)[str(v_form)])
        return dfs
