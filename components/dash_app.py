import dash_mantine_components as dmc
from dash import ClientsideFunction, Input, Output, clientside_callback, dcc, html

from components import navbar, wrapper

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
    "defaultRadius": "md",
    "defaultGradient": {"from": "SVAzul", "to": "BooptLaranja"},
    "fontFamily": "'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif, system-ui;",
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
                dcc.Download(id="download"),
                dcc.Location(id="url", refresh="callback-nav"),
                dcc.Location(id="url-no-refresh", refresh=False),
                html.Div(
                    id="app",
                    children=[
                        wrapper.layout(),
                        navbar.layout(),
                    ],
                ),
            ],
        ),
    )


clientside_callback(
    ClientsideFunction("interacoes", "abrir_barra_lateral"),
    Output("navbar", "children"),
    Input("burger-btn", "opened"),
    prevent_initial_call=True,
)
