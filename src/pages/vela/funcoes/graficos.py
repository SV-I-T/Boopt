from locale import format_string

import dash_ag_grid as dag
import dash_mantine_components as dmc
import plotly.graph_objects as go
import polars as pl


def cartao_nota_total_etapas(df: pl.DataFrame) -> dmc.Card:
    return dmc.Group(
        [
            dmc.Text(
                format_string(
                    "%.1f",
                    df["pontos"].sum(),
                ),
                size=48,
                weight=700,
            ),
            dmc.Text(
                "/" + format_string("%.0f", df["nome"].n_unique() * 10),
                color="grey",
                size=24,
            ),
        ],
        # align="end",
        spacing=0,
        position="center",
        mx="1rem",
    )


def radar(df: pl.DataFrame, theta: str, r: str) -> go.Figure:
    df = pl.concat([df, df.head(1)])
    fig = go.Figure(
        data=go.Scatterpolar(
            theta=df.get_column(theta).to_list(),
            r=df.get_column(r).to_list(),
            mode="lines+markers+text",
            fill="toself",
            marker=go.scatterpolar.Marker(color="#ff7730"),
            name="",
            # hovertemplate="Etapa %{theta}: <b>%{r:.1f}</b><extra></extra>",
            texttemplate="%{r:.1f}",
            textposition="top center",
            textfont=go.scatterpolar.Textfont(size=16),
        ),
        layout=go.Layout(
            polar=go.layout.Polar(
                radialaxis=go.layout.polar.RadialAxis(
                    range=[0, 10],
                    showline=False,
                    angle=90,
                    tickangle=90,
                    tick0=0,
                    dtick=2,
                    tickfont=go.layout.polar.radialaxis.Tickfont(color="gray"),
                ),
                angularaxis=go.layout.polar.AngularAxis(
                    tickfont=go.layout.polar.angularaxis.Tickfont(size=16),
                ),
            ),
            margin=go.layout.Margin(l=30, r=30, b=20, t=20),
            separators=",.",
            font=go.layout.Font(family="Calibri"),
            # title=go.layout.Title(
            #     font=go.layout.title.Font(size=20), x=0.5, automargin=True, y=1
            # ),
            height=300,
            autosize=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def radar_etapas(df: pl.DataFrame) -> go.Figure:
    fig = radar(df.sort("id").drop("id"), "nome", "pontos")
    fig.update_traces(
        go.Scatterpolar(hovertemplate="Etapa %{theta}: <b>%{r:.1f}</b><extra></extra>")
    )
    # fig.update_layout(go.Layout(title="<b>Pontuação por Etapas</b>"))

    return fig


def radar_comp(df: pl.DataFrame) -> go.Figure:
    fig = radar(df.sort("nome"), "nome", "pontos")
    fig.update_traces(
        go.Scatterpolar(
            hovertemplate="%{theta}: <b>%{r:.1f}</b><extra></extra>",
            mode="lines+markers",
            marker=go.scatterpolar.Marker(color="#1618ff"),
        )
    )
    # fig.update_layout(go.Layout(title="<b>Nota por Competência</b>"))
    return fig


def rosca_grupo(df: pl.DataFrame) -> go.Figure:
    df = (
        df.group_by("grupo")
        .agg(pl.count().alias("competencias"))
        .sort("grupo")
        .with_columns(
            pl.col("grupo")
            .replace({"Alta": "#74dc74", "Média": "#edd577", "Baixa": "#f78080"})
            .alias("cor")
        )
    )
    fig = go.Figure(
        data=go.Pie(
            values=df.get_column("competencias").to_list(),
            labels=df.get_column("grupo").to_list(),
            marker=go.pie.Marker(colors=df.get_column("cor").to_list()),
            texttemplate="<b>%{label}</b><br>%{value} (%{percent})",
            direction="clockwise",
            hole=0,
        ),
        layout=go.Layout(
            margin=go.layout.Margin(l=30, r=30, b=30, t=30),
            separators=",.",
            font=go.layout.Font(family="Calibri", size=16),
            # title=go.layout.Title(
            #     text="<b>Competências por Grupo</b>",
            #     font=go.layout.title.Font(size=20),
            #     x=0.5,
            #     automargin=True,
            # ),
            showlegend=False,
            hovermode=False,
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig


def tabela_competencias(df: pl.DataFrame):
    df = df.sort("nome")
    tabela = dag.AgGrid(
        id="tabela-competencias",
        rowData=df.to_dicts(),
        columnDefs=[
            {"field": "nome", "headerName": "Competência"},
            {
                "field": "pontos",
                "headerName": "Nota",
                "valueFormatter": {
                    "function": 'd3.format(".1f")(params.value).replaceAll(".", ",")'
                },
            },
        ],
        defaultColDef={"sortable": True},
        columnSize="sizeToFit",
        className="ag-theme-balham",
        getRowStyle={
            "styleConditions": [
                {
                    "condition": 'params.data.grupo == "Baixa"',
                    "style": {"backgroundColor": "#ffc0c0"},
                },
                {
                    "condition": 'params.data.grupo == "Média"',
                    "style": {"backgroundColor": "#edd577"},
                },
                {
                    "condition": 'params.data.grupo == "Alta"',
                    "style": {"backgroundColor": "#d5fbd5"},
                },
            ]
        },
        dashGridOptions={"suppressRowHoverHighlight": True},
        style={"height": 300},
    )

    return tabela
