import dash_ag_grid as dag
import dash_mantine_components as dmc
import polars as pl
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_chartjs import ChartJs
from dash_iconify import DashIconify

from utils.banco_dados import db
from utils.vela import Vela

register_page(__name__, path="/dashboard", title="DEMO | Dashboard | Vela Assessment")


def layout():
    data_empresas = sorted(db("Respostas").distinct("empresa"))

    painel_filtros = [
        dmc.MultiSelect(
            id="adm-results-vela-empresas",
            label=[
                "Empresas",
                dmc.Button(
                    id="adm-results-vela-empresas-all",
                    children="Todos",
                    compact=True,
                    variant="subtle",
                    size="xs",
                    ml="0.5rem",
                ),
            ],
            placeholder="Selecionar",
            clearable=True,
            data=data_empresas,
        ),
        dmc.MultiSelect(
            id="adm-results-vela-nomes",
            label=[
                "Nome",
                dmc.Button(
                    id="adm-results-vela-nomes-all",
                    children="Todos",
                    compact=True,
                    variant="subtle",
                    size="xs",
                    ml="0.5rem",
                ),
            ],
            placeholder="Selecionar",
            clearable=True,
        ),
        dmc.Button(
            id="adm-results-vela-ok-btn",
            children="Aplicar filtros",
            rightIcon=DashIconify(icon="fluent:arrow-right-24-regular", width=24),
        ),
    ]

    return [
        dmc.Accordion(
            children=dmc.AccordionItem(
                value="filtros",
                children=[
                    dmc.AccordionControl(
                        "Filtros",
                        icon=DashIconify(icon="fluent:filter-24-regular", width=24),
                    ),
                    dmc.AccordionPanel(painel_filtros),
                ],
            ),
            variant="separated",
            radius="xl",
            value="filtros",
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
                html.Div(
                    className="qtd-empresas",
                    children=[
                        html.Span(id="adm-results-vela-qtd-empresas"),
                        html.Label("empresas"),
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
                    },
                    "legend": {"display": False},
                },
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
                "suppressMenu": True,
                "suppressMovable": True,
                "cellStyle": {
                    "function": "params.value && {'backgroundColor': params.value >= 8 ? '#d5fbd5': params.value < 5 ? '#ffc0c0' : '#fff'}"
                },
            },
            className="ag-theme-quartz compact",
        ),
    ]


clientside_callback(
    ClientsideFunction("clientside", "selecionar_todos"),
    Output("adm-results-vela-empresas", "value"),
    Input("adm-results-vela-empresas-all", "n_clicks"),
    State("adm-results-vela-empresas", "data"),
    prevent_initial_call=True,
)

clientside_callback(
    ClientsideFunction("clientside", "selecionar_todos"),
    Output("adm-results-vela-nomes", "value"),
    Input("adm-results-vela-nomes-all", "n_clicks"),
    State("adm-results-vela-nomes", "data"),
    prevent_initial_call=True,
)


def consultar_nomes(empresas: list[str]) -> list[str]:
    return db("Respostas").distinct("usuario", {"empresa": {"$in": empresas}})


@callback(
    Output("adm-results-vela-nomes", "data"),
    Input("adm-results-vela-empresas", "value"),
    prevent_initial_call=True,
)
def atualizar_nomes(empresas: list[str]):
    return consultar_nomes(empresas)


@callback(
    Output("adm-results-vela-nota-media", "children"),
    Output("adm-results-vela-qtd-respostas", "children"),
    Output("adm-results-vela-qtd-empresas", "children"),
    Output("adm-results-vela-etapas", "data"),
    Output("adm-results-vela-competencias", "data"),
    Output("adm-results-vela-table", "columnDefs"),
    Output("adm-results-vela-table", "rowData"),
    Input("adm-results-vela-ok-btn", "n_clicks"),
    State("adm-results-vela-nomes", "value"),
    prevent_initial_call=True,
)
def atualizar_dashboard_adm_vela_resultados(n: int, nomes: list[str]):
    if not n:
        raise PreventUpdate
    if not nomes:
        return (
            None,
            None,
            None,
            {"datasets": [], "labels": []},
            {"datasets": [], "labels": []},
            [],
            [],
        )
    aplicacoes = consultar_df_respostas_aplicacoes(nomes)

    dfs = Vela.carregar_formulario()

    df_respostas = (
        pl.DataFrame(aplicacoes)
        .rename({"_id": "_id_resposta"})
        .unnest("frases")
        .melt(
            id_vars=[
                "usuario",
                "empresa",
                "_id_resposta",
            ],
            variable_name="id_frase",
            value_name="resposta",
        )
        .with_columns(
            pl.col("_id_resposta").map_elements(lambda x: str(x), return_dtype=str),
            pl.col("id_frase").cast(pl.Int64),
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
        .agg(
            pl.col("usuario").first(),
            pl.col("empresa").first(),
            pl.col("etapa").first(),
            pl.col("nota").mean(),
        )
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
                "labels": df_notas_competencias.get_column("nota")
                .map_elements(lambda x: f"{x:.1f}", return_dtype=str)
                .to_list(),
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

    GRID_COLUNAS = [
        {"field": col, "valueFormatter": {"function": "FMT(params.value)"}}
        for col in df_notas_competencias_usuarios.columns
    ]
    GRID_DATA = df_notas_competencias_usuarios.to_dicts()

    NOTA_MEDIA = (
        df_respostas_etapas.group_by("_id_resposta")
        .agg(pl.col("nota").sum())
        .get_column("nota")
        .mean()
    )

    QTD_RESPOSTAS = df_respostas.get_column("_id_resposta").n_unique()
    QTD_EMPRESAS = df_respostas.get_column("empresa").n_unique()

    return (
        f"{NOTA_MEDIA:.1f}",
        QTD_RESPOSTAS,
        QTD_EMPRESAS,
        DATA_NOTAS_ETAPAS,
        DATA_NOTAS_COMPETENCIAS,
        GRID_COLUNAS,
        GRID_DATA,
    )


def consultar_df_respostas_aplicacoes(nomes: list[str]):
    aplicacoes = list(
        db("Respostas").aggregate(
            [
                {"$match": {"usuario": {"$in": nomes}}},
                {"$set": {"_id": {"$toString": "$_id"}}},
                {"$project": {"nota": 0}},
            ]
        )
    )
    return aplicacoes
