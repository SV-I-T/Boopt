import dash_mantine_components as dmc
from components.navbar import layout_navbar
from dash import (
    ClientsideFunction,
    Input,
    Output,
    clientside_callback,
    dcc,
    html,
    page_container,
)

TEMA_PADRAO = {
    "colors": {
        "SVAzul": [
            "#eaeaff",
            "#cfd0ff",
            "#9b9cff",
            "#6366ff",
            "#3637ff",
            "#181aff",
            "#030aff",
            "#0000e5",
            "#0000cd",
            "#0000b5",
        ],
        "BooptLaranja": [
            "#fff0e2",
            "#ffdfcc",
            "#ffbd9a",
            "#ff9963",
            "#ff7b36",
            "#ff6718",
            "#ff5c06",
            "#e44d00",
            "#cb4200",
            "#b23600",
        ],
    },
    "primaryColor": "SVAzul",
    "colorScheme": "light",
    "defaultRadius": "lg",
    "defaultGradient": {"from": "SVAzul", "to": "BooptLaranja"},
}


def layout():
    return dmc.MantineProvider(
        id="mantine-provider",
        theme=TEMA_PADRAO,
        withCSSVariables=True,
        withNormalizeCSS=True,
        withGlobalStyles=True,
        inherit=True,
        children=dmc.NotificationsProvider(
            position="top-right",
            zIndex=10000,
            children=[
                html.Div(id="notificacoes"),
                dcc.Store(id="refresh"),
                dcc.Download(id="download"),
                dcc.Location(id="url", refresh="callback-nav"),
                html.Div(
                    id="page-container",
                    children=[
                        layout_navbar(),
                        html.Div(
                            id="wrapper",
                            children=[
                                html.Div(id="frame"),
                                page_container,
                                html.Div(id="navbar-backdrop"),
                            ],
                        ),
                        html.Div(
                            id="burger-header",
                            children=[
                                dmc.Burger(id="burger-btn", opened=False, color="white")
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )


clientside_callback(
    ClientsideFunction("clientside", "abrir_barra_lateral"),
    Output("navbar", "children"),
    Input("burger-btn", "opened"),
    prevent_initial_call=True,
)


clientside_callback(
    ClientsideFunction("clientside", "atualizar_pagina"),
    Output("refresh", "data"),
    Input("refresh", "data"),
    prevent_initial_call=True,
)
