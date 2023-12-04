import dash_mantine_components as dmc
from dash import get_asset_url, html, dcc, callback, Output, Input, page_registry


def layout_header():
    return dmc.Header(
        dmc.Grid(
            [
                dmc.Col(
                    html.Img(src=get_asset_url("imgs/sv/h-azul.svg"), height=50),
                    span="content",
                ),
                dmc.Col(
                    html.Div(
                        id="container-paginas",
                        style={"overflowY": "scroll", "height": 50},
                    ),
                    span="content",
                ),
                dmc.Col(
                    html.Img(
                        src=get_asset_url("imgs/boopt/HORIZONTAL AZUL.png"), height=50
                    ),
                    span="content",
                ),
            ],
            my=0,
            px="0.5rem",
            align="stretch",
            justify="space-between",
        ),
        height="auto",
        fixed=True,
        withBorder=True,
        id="header",
    )


@callback(Output("container-paginas", "children"), Input("url", "href"))
def listar_paginas(_):
    return [
        html.Div(
            [page["name"], "-", dcc.Link(href=page["path"])], style={"font-size": 10}
        )
        for page in page_registry.values()
    ]
