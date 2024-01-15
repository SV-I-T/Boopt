import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, get_asset_url, html, page_registry


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
                        style={"height": 50},
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


@callback(Output("container-paginas", "children"), Input("url", "pathname"))
def listar_paginas(path):
    return dmc.Menu(
        [
            dmc.MenuTarget(dmc.Button("Páginas", variant="light")),
            dmc.MenuDropdown(
                [
                    dmc.MenuItem(
                        f'{page["name"]} [~{page["path"]}]',
                        href=page["path"],
                        target="_self",
                        color="grey" if path == page["path"] else False,
                    )
                    for page in page_registry.values()
                ]
            ),
        ]
    )
