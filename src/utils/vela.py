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
    descricao: str = ""
    v_form: Optional[int] = 1
    empresa: ObjectId
    participantes: list[ObjectId] = Field(default_factory=list)

    class Config:
        str_strip_whitespace = True
        arbitrary_types_allowed = True

    def registrar(self) -> None:
        r = db("VelaAplicações").insert_one(self.model_dump(exclude={"id_"}))
        assert r.acknowledged, "Ocorreu algo de errado. Tente novamente mais tarde."

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
    def consultar_dfs_resposta(cls, id_resposta: str | ObjectId) -> list[pl.DataFrame]:
        r = db("Respostas").find_one(
            {"_id": ObjectId(id_resposta)},
            {"nota": 0},
        )

        df_resposta = (
            pl.DataFrame(r)
            .unnest("frases")
            .unpivot(pl.selectors.digit(), variable_name="id_frase", value_name="nota")
            .with_columns(pl.col("id_frase").cast(pl.Int64))
        )

        dfs = Vela.carregar_formulario()

        df_competencias = (
            df_resposta.join(dfs.competencias, left_on="id_frase", right_on="id")
            .with_columns(
                pl.col("notas").list.get(pl.col("nota").sub(1)).alias("pontos")
            )
            .drop("id_frase", "nota", "notas", "desc")
            .group_by("nome")
            .agg(pl.col("pontos").mean())
            .sort("nome")
        )

        df_etapas = (
            df_competencias.join(
                dfs.etapas, left_on="nome", right_on="competencias", how="right"
            )
            .group_by("id")
            .agg(pl.col("nome").first(), pl.col("pontos").mean())
            .sort("id")
        )

        return df_competencias, df_etapas

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
