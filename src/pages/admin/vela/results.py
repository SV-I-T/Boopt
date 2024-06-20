import dash_ag_grid as dag
import dash_mantine_components as dmc
import polars as pl
from bson import ObjectId
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_chartjs import ChartJs
from dash_iconify import DashIconify
from icecream import ic
from utils.banco_dados import db
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario
from utils.vela import VelaAssessment

register_page(
    __name__, path="/app/admin/vela/results", title="ADM - Resultados Vela Assessment"
)


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout():
    usr_atual = Usuario.atual()

    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]

    data_aplicacao = consultar_assessments_disponiveis(usr_atual, usr_atual.empresa)

    return [
        dmc.Group(
            children=[
                dmc.Select(
                    id="adm-results-vela-empresa",
                    data=data_empresas,
                    value=str(usr_atual.empresa),
                    icon=DashIconify(icon="fluent:building-24-regular", width=24),
                    searchable=True,
                    nothingFound="Não encontramos nada",
                    display="block"
                    and (usr_atual.role in (Role.DEV, Role.CONS))
                    or "none",
                ),
                dmc.MultiSelect(id="adm-results-vela-aplicacao", data=data_aplicacao),
            ]
        ),
        html.Div(
            className="vela-card-metricas",
            children=[
                html.Div(
                    className="nota-media",
                    children=[
                        html.Label("Nota média"),
                        html.Span(id="adm-results-vela-nota-media"),
                        html.Span("/70"),
                    ],
                ),
                html.Div(
                    className="qtd-respostas",
                    children=[
                        html.Span(id="adm-results-vela-qtd-respostas"),
                        html.Label("respostas"),
                    ],
                ),
            ],
        ),
        ChartJs(
            id="adm-results-vela-etapas",
            type="bar",
            data={"datasets": [], "labels": []},
            options={
                "scales": {"y": {"max": 10, "min": 0}},
                "plugins": {
                    "datalabels": {
                        "align": "end",
                        "anchor": "end",
                        "color": "#fff",
                        "borderRadius": 4,
                        "backgroundColor": "#1618ff",
                    },
                },
            },
            style={"display": "none"},
        ),
        ChartJs(
            id="adm-results-vela-competencias",
            type="polarArea",
            data={"datasets": [], "labels": []},
            options={
                "scales": {
                    "r": {
                        "max": 10,
                        "min": 0,
                        "pointLabels": {"display": True, "centerPointLabels": True},
                        "angleLines": {"display": True},
                        "ticks": {"z": 10},
                    },
                },
                "plugins": {
                    "datalabels": {
                        "align": "end",
                        "anchor": "end",
                        "color": "#fff",
                        "borderRadius": 4,
                        "formatter": "function(value, context) {return context.dataIndex;}",
                    },
                    "legend": {"display": False},
                },
                "responsive": True,
                "aspectRatio": 1,
            },
        ),
        dag.AgGrid(
            id="adm-results-vela-table",
            dashGridOptions={
                "overlayLoadingTemplate": {
                    "function": "'<span>Não há registros</span>'"
                },
                "overlayNoRowsTemplate": {
                    "function": "'<span>Não há registros</span>'"
                },
            },
            defaultColDef={
                "filter": True,
                "floatingFilterComponentParams": {
                    "suppressFilterButton": True,
                },
                "suppressMenu": True,
                "suppressMovable": True,
                "cellStyle": {
                    "function": "params.value && {'backgroundColor': params.value >= 8 ? '#d5fbd5': params.value < 5 ? '#ffc0c0' : '#fff'}"
                },
            },
            className="ag-theme-quartz compact",
        ),
    ]


@callback(
    Output("adm-results-vela-nota-media", "children"),
    Output("adm-results-vela-qtd-respostas", "children"),
    Output("adm-results-vela-etapas", "data"),
    Output("adm-results-vela-competencias", "data"),
    Output("adm-results-vela-table", "columnDefs"),
    Output("adm-results-vela-table", "rowData"),
    Input("adm-results-vela-aplicacao", "value"),
)
def atualizar_dashboard_adm_vela_resultados(ids_aplicacao: list[str]):
    if not ids_aplicacao:
        return (
            None,
            None,
            {"datasets": [], "labels": []},
            {"datasets": [], "labels": []},
            [],
            [],
        )
    aplicacoes = consultar_df_respostas_aplicacoes(
        [ObjectId(id) for id in ids_aplicacao]
    )

    dfs = VelaAssessment.carregar_formulario()

    df_respostas = (
        pl.DataFrame(aplicacoes)
        .select(pl.all().name.suffix("_aplicacao"))
        .explode("respostas_aplicacao")
        .unnest("respostas_aplicacao")
        .rename({"_id": "_id_resposta"})
        .unnest("frases")
        .melt(
            id_vars=[
                "_id_aplicacao",
                "descricao_aplicacao",
                "v_form_aplicacao",
                "id_usuario",
                "usuario",
                "_id_resposta",
            ],
            variable_name="id_frase",
            value_name="resposta",
        )
        .with_columns(
            pl.col("_id_aplicacao", "_id_resposta", "id_usuario").map_elements(
                lambda x: str(x), return_dtype=str
            ),
            pl.col("id_frase").cast(pl.Int64),
            pl.col("usuario").list.first(),
        )
        .join(dfs.competencias, left_on="id_frase", right_on="id", how="left")
        .with_columns(pl.col("notas").list.get(pl.col("resposta").sub(1)).alias("nota"))
        .drop("resposta", "notas")
        .rename({"nome": "competencias", "desc": "frase"})
    )

    df_respostas_etapas = (
        df_respostas.join(dfs.etapas, on="competencias", how="left")
        .rename({"nome": "etapa", "id": "id_etapa", "peso": "peso_etapa"})
        .group_by("_id_resposta", "id_etapa")
        .agg(pl.col("usuario").first(), pl.col("etapa").first(), pl.col("nota").mean())
    )

    df_notas_etapas = (
        df_respostas_etapas.sort("id_etapa")
        .group_by("etapa", maintain_order=True)
        .agg(pl.col("nota").mean())
    )
    DATA_NOTAS_ETAPAS = {
        "labels": df_notas_etapas.get_column("etapa").to_list(),
        "datasets": [
            {
                "label": "Nota média",
                "data": df_notas_etapas.get_column("nota").round(1).to_list(),
                "backgroundColor": "#1618ff",
            }
        ],
    }

    df_notas_competencias = (
        df_respostas.group_by("competencias")
        .agg(pl.col("nota").mean())
        .with_columns(
            pl.when(pl.col("nota").ge(8))
            .then(pl.lit("#57b956"))
            .when(pl.col("nota").lt(5))
            .then(pl.lit("#d23535"))
            .otherwise(pl.lit("#b3b3b3"))
            .alias("cor")
        )
        .sort("competencias")
    )

    DATA_NOTAS_COMPETENCIAS = {
        "labels": df_notas_competencias.get_column("competencias").to_list(),
        "datasets": [
            {
                "label": "Nota média",
                "data": df_notas_competencias.get_column("nota").round(1).to_list(),
                "backgroundColor": df_notas_competencias.get_column("cor").to_list(),
                "datalabels": {
                    "backgroundColor": df_notas_competencias.get_column(
                        "cor"
                    ).to_list(),
                },
                "labels": df_notas_competencias.get_column("nota").round(0).to_list(),
            }
        ],
    }

    df_notas_competencias_usuarios = (
        df_respostas.sort("competencias", "usuario")
        .group_by("competencias", "usuario", maintain_order=True)
        .agg(pl.col("nota").mean())
        .pivot(values="nota", index="usuario", columns="competencias")
        .with_columns(pl.col(pl.NUMERIC_DTYPES).round(1))
    )

    GRID_COLUNAS = [{"field": col} for col in df_notas_competencias_usuarios.columns]
    GRID_DATA = df_notas_competencias_usuarios.to_dicts()

    NOTA_MEDIA = (
        df_respostas_etapas.group_by("_id_resposta")
        .agg(pl.col("nota").sum())
        .get_column("nota")
        .mean()
    )

    QTD_RESPOSTAS = df_respostas.get_column("_id_resposta").n_unique()

    return (
        f"{NOTA_MEDIA:.1f}",
        QTD_RESPOSTAS,
        DATA_NOTAS_ETAPAS,
        DATA_NOTAS_COMPETENCIAS,
        GRID_COLUNAS,
        GRID_DATA,
    )


def consultar_df_respostas_aplicacoes(ids_aplicacao: list[ObjectId]):
    aplicacoes = list(
        db("Boopt", "VelaAplicações").aggregate(
            [
                {"$match": {"_id": {"$in": ids_aplicacao}}},
                {
                    "$lookup": {
                        "from": "VelaRespostas",
                        "let": {"id_aplicacao": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$id_aplicacao", "$$id_aplicacao"]
                                    }
                                }
                            },
                            {
                                "$lookup": {
                                    "from": "Usuários",
                                    "localField": "id_usuario",
                                    "foreignField": "_id",
                                    "as": "usuario",
                                },
                            },
                            {
                                "$set": {
                                    "id_usuario": {"$toString": "$id_usuario"},
                                    "_id": {"$toString": "$_id"},
                                    "usuario": "$usuario.nome",
                                }
                            },
                        ],
                        "localField": "_id",
                        "foreignField": "id_aplicacao",
                        "as": "respostas",
                    }
                },
                {
                    "$project": {
                        "participantes": 0,
                        "empresa": 0,
                        "respostas": {
                            "nota": 0,
                            "id_aplicacao": 0,
                        },
                    }
                },
            ]
        )
    )

    return aplicacoes


def consultar_assessments_disponiveis(usr: Usuario, id_empresa: str):
    return list(
        db("Boopt", "VelaAplicações").aggregate(
            [
                {"$match": {"empresa": ObjectId(id_empresa)}},
                {
                    "$project": {
                        "_id": 0,
                        "value": {"$toString": "$_id"},
                        "label": {
                            "$concat": [
                                {
                                    "$dateToString": {
                                        "date": {"$toDate": "$_id"},
                                        "format": "(%d/%m/%Y) - ",
                                    }
                                },
                                "$descricao",
                            ]
                        },
                    }
                },
            ]
        )
    )
