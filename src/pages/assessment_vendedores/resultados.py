import dash_mantine_components as dmc
import polars as pl
from dash import dcc, register_page
from utils.banco_dados import db
from utils.cache import cache

from .funcoes.cpf import layout_cpf
from .funcoes.graficos import (
    cartao_nota_total_etapas,
    radar_comp,
    radar_etapas,
    rosca_grupo,
    tabela_competencias,
)

register_page(
    __name__,
    path="/assessment-vendedor/resultados",
    title="Resultados - Assessment Vendedor",
)


def layout(cpf: str = None):
    if not cpf:
        return layout_cpf
    else:
        dfs = buscar_resposta(cpf)
        if dfs is None:
            return dmc.Alert(
                "Este CPF não possui respostas", title="Erro!", color="red"
            )
        else:
            df_notas_etapas, df_notas_competencias = dfs

        return dmc.Container(
            [
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Group(
                                [
                                    dmc.Avatar(
                                        "1",
                                        color="BooptLaranja",
                                        radius="xl",
                                    ),
                                    dmc.Text("Sua nota:", weight=700),
                                    cartao_nota_total_etapas(df_notas_etapas),
                                ]
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            dmc.Group(
                                [
                                    dmc.Avatar(
                                        "2",
                                        color="BooptLaranja",
                                        radius="xl",
                                    ),
                                    dmc.Text(
                                        "Pontuação por Etapa do Atendimento Comercial",
                                        weight=700,
                                    ),
                                ]
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=radar_etapas(df_notas_etapas),
                                config=dict(displayModeBar=False, locale="pt-br"),
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        dmc.Avatar(
                                            "3",
                                            color="BooptLaranja",
                                            radius="xl",
                                        ),
                                        dmc.Text(
                                            "Competências por Grupo",
                                            weight=700,
                                        ),
                                    ]
                                ),
                                dmc.Group(
                                    [
                                        dmc.Text(
                                            "Competência baixa: Nota 0 a 5",
                                            color="red",
                                            size="sm",
                                        ),
                                        dmc.Text(
                                            "Competência média: Nota 6 a 7",
                                            color="yellow",
                                            size="sm",
                                        ),
                                        dmc.Text(
                                            "Competência alta: Nota 8 a 10",
                                            color="green",
                                            size="sm",
                                        ),
                                    ]
                                ),
                            ],
                            span=12,
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=rosca_grupo(df_notas_competencias),
                                config=dict(displayModeBar=False, locale="pt-br"),
                            ),
                            sm=6,
                        ),
                        dmc.Col(tabela_competencias(df_notas_competencias), sm=6),
                        dmc.Col(
                            dmc.Group(
                                [
                                    dmc.Avatar(
                                        "4",
                                        color="BooptLaranja",
                                        radius="xl",
                                    ),
                                    dmc.Text("Nota por Competência:", weight=700),
                                ]
                            ),
                            span=12,
                        ),
                        dmc.Col(
                            dcc.Graph(
                                figure=radar_comp(df_notas_competencias),
                                config=dict(displayModeBar=False, locale="pt-br"),
                            ),
                        ),
                    ]
                ),
            ]
        )


@cache.memoize(timeout=6000)
def buscar_resposta(cpf: str):
    respostas = list(
        db("AssessmentVendedores", "Respostas").aggregate(
            [
                {"$match": {"cpf": cpf}},
                {"$addFields": {"dt": {"$toDate": "$_id"}}},
                {"$sort": {"dt": 1}},
                {
                    "$lookup": {
                        "from": "Aplicações",
                        "localField": "id_aplicacao",
                        "foreignField": "_id",
                        "as": "aplicação",
                    }
                },
                {
                    "$lookup": {
                        "from": "Formulários",
                        "localField": "aplicação.id_form",
                        "foreignField": "_id",
                        "as": "form",
                    }
                },
                {"$unwind": {"path": "$aplicação", "preserveNullAndEmptyArrays": True}},
                {"$unwind": {"path": "$form", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "id_aplicacao": 1,
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
    )

    if len(respostas) == 0:
        return None
    else:
        df_notas_etapas = pl.DataFrame()
        df_notas_competencias = pl.DataFrame()

        for resposta in respostas:
            form = resposta["form"]

            df_notas = pl.DataFrame(resposta["notas"])
            df_competencias = (
                pl.DataFrame(form["competencias"]).explode("frases").unnest("frases")
            )
            df_etapas = pl.DataFrame(form["etapas"]).explode("competencias")

            _df_notas_competencias = (
                df_competencias.join(df_notas, on="id", how="left")
                .group_by("nome")
                .agg(pl.col("notas").list.get(pl.col("nota").sub(1)).mean())
            ).with_columns(
                pl.when(pl.col("notas").lt(5))
                .then(pl.lit("Baixa"))
                .when(pl.col("notas").lt(8))
                .then(pl.lit("Média"))
                .otherwise(pl.lit("Alta"))
                .alias("grupo")
            )
            _df_notas_etapas = (
                df_etapas.join(
                    _df_notas_competencias,
                    left_on="competencias",
                    right_on="nome",
                    how="left",
                )
                .group_by("nome")
                .agg(
                    [
                        pl.col("peso")
                        .mul(pl.col("notas"))
                        .sum()
                        .truediv(pl.col("peso").sum())
                        .alias("nota"),
                        pl.col("id").max(),
                    ]
                )
            )

            df_notas_competencias = pl.concat(
                [df_notas_competencias, _df_notas_competencias], how="diagonal_relaxed"
            ).drop_nulls("nome")
            df_notas_etapas = pl.concat(
                [df_notas_etapas, _df_notas_etapas], how="diagonal_relaxed"
            ).drop_nulls("nome")

        return df_notas_etapas, df_notas_competencias
