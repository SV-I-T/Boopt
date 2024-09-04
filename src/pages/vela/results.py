import plotly.graph_objects as go
import polars as pl
from dash import dcc, get_asset_url, html, register_page

from utils.plotly import get_plotly_configs
from utils.vela import Vela

register_page(
    __name__,
    path_template="/report/<id_resposta>",
    title="[DEMO] Resultados - Vela Assessment",
)


def layout(id_resposta: str):
    df_competencias, df_etapas = Vela.consultar_dfs_resposta(id_resposta)
    nota = df_etapas.get_column("pontos").sum()
    nota_pct = nota / 70
    return [
        html.Div(
            className="vela-report",
            style={"margin-top": "7rem"},
            children=[
                html.H1("Análise do perfil comercial", className="titulo-pagina"),
                html.Div(
                    className="potencial",
                    children=[
                        html.Div(
                            className="rosca",
                            children=[
                                construir_grafico_progresso(nota_pct),
                                html.Img(
                                    src=get_asset_url("imgs/vela/logo.svg"),
                                    alt="Logo Vela",
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=f"{nota_pct:.0%}", className="nota-pct"
                                ),
                                html.Div("POTENCIAL DE SUCESSO"),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    className="plot-box",
                    children=[
                        html.H1("Pontuação por etapa do atendimento"),
                        construir_grafico_etapas(df_etapas),
                    ],
                ),
                html.Div(
                    className="plot-box",
                    children=[
                        html.H1("Pontuação por competência comercial"),
                        construir_grafico_competencias_polar(df_competencias),
                    ],
                ),
                html.Div(
                    className="plot-box",
                    children=[
                        html.H1("Pontuação por competência comercial"),
                        construir_grafico_competencias(df_competencias),
                    ],
                ),
            ],
        ),
    ]


def construir_grafico_progresso(nota_pct: float) -> dcc.Graph:
    # nota_pct = 1
    return dcc.Graph(
        figure=go.Figure(
            data=go.Pie(
                values=[nota_pct, 1 - nota_pct],
                labels=["a", "b"],
                marker=go.pie.Marker(colors=["#FF7730", "#d3d3d3"]),
                hole=0.7,
                textinfo="none",
                sort=False,
            ),
            layout=go.Layout(
                legend=go.layout.Legend(visible=False),
                margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                height=160,
                width=160,
            ),
        ),
        responsive=False,
        config=get_plotly_configs(staticPlot=True, responsive=False, autosizable=False),
    )


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
                    marker=go.bar.Marker(
                        color=[
                            "#f54323",
                            "#fac82c",
                            "#f5183f",
                            "#1840f5",
                            "#45a089",
                            "#6818f5",
                            "#6b5f49",
                        ]
                    ),
                    customdata=df.select("desc").to_numpy(),
                    name="",
                    hovertemplate="<b>%{customdata[0]}</b>: %{y:.1f}",
                    textfont=go.bar.Textfont(color="#fff", size=18),
                    texttemplate="%{y:.1f}",
                ),
            ],
            layout=go.Layout(
                yaxis=go.layout.YAxis(showticklabels=False),
                barmode="overlay",
                legend=go.layout.Legend(visible=False),
                margin=go.layout.Margin(l=0, r=0, b=20, t=20),
                height=300,
            ),
        ),
        config=get_plotly_configs("A PONTE - Vela"),
    )


def construir_grafico_competencias_polar(df: pl.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Barpolar(
                    theta=df_categoria.select(pl.col("nome").str.replace(" ", "<br>"))
                    .get_column("nome")
                    .to_list(),
                    r=df_categoria.get_column("pontos").to_list(),
                    hovertemplate="<b>%{theta}</b>: %{r:.1f}",
                    name=categoria[0],
                    marker=go.barpolar.Marker(
                        color=df_categoria.get_column("Cor").max()
                    ),
                )
                for categoria, df_categoria in df.sort(
                    "pontos", descending=True
                ).group_by("Categoria", maintain_order=True)
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
                height=500,
                legend=go.layout.Legend(
                    x=0.5,
                    y=1,
                    xanchor="auto",
                    yanchor="top",
                    orientation="h",
                    xref="container",
                    yref="container",
                ),
                dragmode="zoom",
            ),
        ),
        config=get_plotly_configs("A PONTE - Competências comerciaias"),
    )


def construir_grafico_competencias(df: pl.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    y=df_categoria.select(pl.col("nome").str.replace(" ", "<br>"))
                    .get_column("nome")
                    .to_list(),
                    x=df_categoria.get_column("pontos").to_list(),
                    orientation="h",
                    hovertemplate="<b>%{y}</b>: %{x:.1f}",
                    name=categoria[0],
                    marker=go.bar.Marker(color=df_categoria.get_column("Cor").max()),
                    texttemplate="%{x:.1f}",
                    textfont=go.bar.Textfont(
                        color="black" if categoria[0] == "Regular" else "white", size=20
                    ),
                )
                for categoria, df_categoria in df.sort(
                    "pontos", descending=True
                ).group_by("Categoria", maintain_order=True)
            ],
            layout=go.Layout(
                yaxis=go.layout.YAxis(
                    categoryorder="category descending",
                    automargin="left",
                    ticklabelstandoff=10,
                    tickfont=go.layout.yaxis.Tickfont(size=12),
                    # ticklabelposition="inside",
                ),
                legend=go.layout.Legend(
                    x=0.5,
                    y=1,
                    yanchor="top",
                    xanchor="center",
                    # yanchor="bottom",
                    orientation="h",
                    xref="container",
                    yref="container",
                ),
                height=700,
                xaxis=go.layout.XAxis(range=[0, 10]),
                margin=go.layout.Margin(l=0, r=0, t=0, b=0),
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
