from dash import (
    Dash,
    html,
    dcc,
    page_container,
    get_asset_url,
    page_registry,
    callback,
    Output,
    Input,
)
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc

from components.header import layout_header

app = Dash(
    __name__,
    server=False,
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
    use_pages=True,
    update_title=None,
)

app.layout = dmc.MantineProvider(
    dmc.NotificationsProvider(
        [
            html.Div(id="notifications"),
            dcc.Location(id="url", refresh=True),
            layout_header(),
            dmc.Container(
                [
                    dmc.Paper(
                        [
                            dmc.Grid(
                                [
                                    dmc.Col(
                                        dmc.Title("Assessment Vendedor", order=2),
                                        span="content",
                                    ),
                                    dmc.Col(
                                        dmc.Image(
                                            get_asset_url(
                                                "imgs/boopt/HORIZONTAL AZUL.png"
                                            ),
                                            height=30,
                                        ),
                                        span="content",
                                    ),
                                ],
                                align="center",
                                justify="space-between",
                            ),
                            dmc.Divider(mt="1rem", mb="2rem"),
                            page_container,
                        ],
                        shadow="md",
                        p="1rem",
                        withBorder=True,
                    )
                ],
                mb="2rem",
                mt=100,
            ),
        ]
    ),
    id="mantine-provider",
    theme={
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
    },
    withCSSVariables=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    inherit=True,
)
