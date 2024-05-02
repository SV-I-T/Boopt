import dash_mantine_components as dmc
import polars as pl
from bson import ObjectId
from dash import dcc, register_page
from dash_iconify import DashIconify
from utils.cache import cache
from utils.modelo_assessment import VelaAssessment
from utils.modelo_usuario import Role, Usuario, checar_perfil, layout_nao_autorizado

from .funcoes.graficos import (
    cartao_nota_total_etapas,
    radar_comp,
    radar_etapas,
    rosca_grupo,
)

register_page(
    __name__,
    path="/app/vela/resultado",
    title="Resultados - Vela Assessment",
)


@checar_perfil
def layout(usr: str = None, resposta: str = None):
    usr_atual = Usuario.atual()

    if usr == usr_atual.id:
        # O usuário que está tentando acessar é o dono da resposta
        pass
    elif usr_atual.perfil in [Role.DEV]:
        # O usuário que está tentando acessar é admin
        pass
    elif (
        usr_atual.perfil == Role.ADM
        and usr_atual.empresa == Usuario.buscar("_id", usr).empresa
    ):
        # O usuário que está tentando acessar é gestor da empresa do dono da resposta
        pass
    else:
        # O usuário que está tentando acessar não tem permissão
        return layout_nao_autorizado()

    respostas = VelaAssessment.buscar_respostas(ObjectId(usr))

    return dmc.Container(
        [
            dmc.Text("Aplicação:", span=True, weight=500, mr="0.5rem"),
            dmc.Menu(
                [
                    dmc.MenuTarget(
                        dmc.Button(
                            variant="white",
                            compact=True,
                            rightIcon=DashIconify(
                                icon="fluent:chevron-down-20-filled", width=20
                            ),
                            children=ObjectId(resposta)
                            .generation_time.date()
                            .strftime(
                                "%d de %B de %Y",
                            ),
                        )
                    ),
                    dmc.MenuDropdown(
                        [
                            dmc.MenuItem(
                                children=resposta_.generation_time.date().strftime(
                                    "%d de %B de %Y",
                                ),
                                href=f"/app/vela/resultado/?usr={usr}&resposta={resposta_}",
                            )
                            if str(resposta_) != resposta
                            else None
                            for resposta_ in respostas
                        ]
                    ),
                ],
            ),
            dmc.Grid(
                id="resultados-assessment",
                children=construir_resultados(resposta),
            ),
        ]
    )


def construir_resultados(id_resposta: str):
    dfs = dfs_resultado(id_resposta)

    if dfs is None:
        return dmc.Alert("Esta resposta não existe", title="Erro!", color="red")
    else:
        df_notas_etapas, df_notas_competencias = dfs

    return [
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
        dcc.Graph(
            figure=radar_etapas(df_notas_etapas),
            config=dict(displayModeBar=False, locale="pt-br"),
        ),
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
        dcc.Graph(
            figure=rosca_grupo(df_notas_competencias),
            config=dict(displayModeBar=False, locale="pt-br"),
        ),
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
        dcc.Graph(
            figure=radar_comp(df_notas_competencias),
            config=dict(displayModeBar=False, locale="pt-br"),
        ),
    ]


@cache.memoize(timeout=6000)
def dfs_resultado(id_resposta: str):
    resposta = VelaAssessment.resultado(ObjectId(id_resposta))

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
