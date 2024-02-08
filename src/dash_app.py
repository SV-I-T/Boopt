import dash_mantine_components as dmc
from components.header import layout_header
from dash import dcc, html, page_container

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
            position="bottom-center",
            children=[
                html.Div(id="notificacoes"),
                dcc.Download(id="download"),
                dcc.Location(id="url", refresh=True),
                layout_header(),
                html.Div(
                    page_container, style={"margin": "2rem", "margin-top": "5rem"}
                ),
            ],
        ),
    )
