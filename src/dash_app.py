import dash_mantine_components as dmc
from dash import dcc, get_asset_url, html, page_container

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
        children=[
            dcc.Location(id="url", refresh="callback-nav"),
            html.Div(
                id="app",
                children=[
                    html.Div(
                        id="wrapper",
                        children=[
                            html.Header(
                                children=[
                                    dmc.Anchor(
                                        html.Div(
                                            className="logo-boopt",
                                            children="Logo Boopt",
                                        ),
                                        href="/",
                                    ),
                                    html.Div("VERSÃO BETA", className="beta-tag"),
                                ]
                            ),
                            page_container,
                        ],
                    ),
                ],
            ),
        ],
    )
