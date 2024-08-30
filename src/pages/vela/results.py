import plotly.graph_objects as go
import polars as pl
from dash import dcc, html, register_page

from utils.plotly import get_plotly_configs
from utils.vela import Vela

register_page(
    __name__,
    path_template="/report/<id_resposta>",
    title="[DEMO] Resultados - Vela Assessment",
)


def layout(id_resposta: str):
    df_competencias, df_etapas = Vela.consultar_dfs_resposta(id_resposta)
    return [
        html.Div(
            className="vela-report",
            style={"margin-top": "7rem"},
            children=[
                html.Div(
                    className="nota-pct",
                    children=f'{df_etapas.get_column("pontos").sum() / 70:.0%}',
                ),
                construir_grafico_etapas(df_etapas),
                construir_grafico_competencias(df_competencias),
            ],
        ),
    ]


def construir_grafico_etapas(df: pl.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df.get_column("nome").to_list(),
                    y=[10 for _ in range(df.shape[0])],
                    marker=go.bar.Marker(color="#ddd"),
                    name="",
                    hoverinfo="skip",
                ),
                go.Bar(
                    x=df.get_column("nome").to_list(),
                    y=df.get_column("pontos").to_list(),
                    customdata=df.select("desc").to_numpy(),
                    name="",
                    hovertemplate="<b>%{customdata[0]}</b>: %{y:.1f}",
                    textfont=go.bar.Textfont(color="#fff", size=18),
                    texttemplate="%{y:.1f}",
                ),
            ],
            layout=go.Layout(
                title=go.layout.Title(text="<b>Pontuação por etapa do atendimento</b>"),
                yaxis=go.layout.YAxis(range=[0, 10]),
                barmode="overlay",
                legend=go.layout.Legend(visible=False),
                hovermode="x",
            ),
        ),
        config=get_plotly_configs("A PONTE - Vela"),
    )


def construir_grafico_competencias(df: pl.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Barpolar(
                    theta=df_categoria.get_column("nome").to_list(),
                    r=df_categoria.get_column("pontos").to_list(),
                    hovertemplate="<b>%{theta}</b>: %{r:.1f}",
                    name=categoria[0],
                    marker=go.barpolar.Marker(
                        color=df_categoria.get_column("Cor").max()
                    ),
                )
                for categoria, df_categoria in df.group_by("Categoria")
            ],
            layout=go.Layout(
                polar=go.layout.Polar(
                    radialaxis=go.layout.polar.RadialAxis(
                        range=[0, 10], angle=90, tickangle=90
                    ),
                    angularaxis=go.layout.polar.AngularAxis(
                        rotation=90,
                        direction="clockwise",
                        categoryorder="category ascending",
                    ),
                ),
                title=go.layout.Title(
                    text="<b>Pontuação das competências comerciais</b>"
                ),
                height=550,
            ),
        ),
        config=get_plotly_configs("A PONTE - Competências comerciaias"),
    )


def construir_tabela(df: pl.DataFrame) -> html.Table:
    return html.Table(
        children=[
            html.Thead(html.Tr(children=[html.Th(col) for col in df.columns])),
            html.Tbody(
                children=[
                    html.Tr(children=[html.Td(el) for el in row]) for row in df.rows()
                ]
            ),
        ]
    )
