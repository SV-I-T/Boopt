import dash_mantine_components as dmc
from components.header import layout_header
from dash import dcc, get_asset_url, html, page_container


def layout():
    return dmc.MantineProvider(
        dmc.NotificationsProvider(
            [
                html.Div(id="notifications"),
                dcc.Location(id="url", refresh=True),
                layout_header(),
                dmc.Title("Assessment Vendedor", order=2),
                dmc.Divider(mt="1rem", mb="2rem"),
                page_container,
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
