import dash_mantine_components as dmc
from dash import get_asset_url, html


def layout():
    return html.Header(
        id="burger-header",
        children=[
            dmc.Anchor(
                children=html.Img(
                    src=get_asset_url("assets/boopt/horizontal_branco.svg"),
                    alt="Logo Boopt",
                ),
                href="/app/vela",
            ),
            dmc.Burger(id="burger-btn", opened=False, color="white"),
        ],
    )
