import dash_mantine_components as dmc
import polars as pl
from bson import ObjectId
from dash import dcc, register_page
from utils.banco_dados import db
from utils.cache import cache
from utils.modelo_assessment import AssessmentVendedor

from .funcoes.graficos import (
    cartao_nota_total_etapas,
    radar_comp,
    radar_etapas,
    rosca_grupo,
    tabela_competencias,
)

register_page(
    __name__,
    path="/app/assessment-vendedor/resultado",
    title="Resultados - Assessment Vendedor",
)


def layout(id: str = None):
    dfs = dfs_resultado(id)
    if dfs is None:
        return dmc.Alert("Este CPF não possui respostas", title="Erro!", color="red")
    else:
        df_notas_etapas, df_notas_competencias = dfs

    return dmc.Container(
        [
            dmc.Select(
                id="select-id-resposta",
                label="Data de envio",
                value=id,
                data=[{"value": id, "label": ObjectId(id).generation_time.date()}],
                w=150,
            ),
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


# @cache.memoize(timeout=6000)
def dfs_resultado(id_resposta: str):
    resposta = AssessmentVendedor.resultado(ObjectId(id_resposta))

    if resposta is None:
        return None

    else:
        df_notas_etapas = pl.DataFrame()
        df_notas_competencias = pl.DataFrame()

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
