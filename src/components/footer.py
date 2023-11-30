import dash_mantine_components as dmc
from dash import get_asset_url


def layout_footer():
    return dmc.Footer(
        [dmc.Image(get_asset_url("imgs/sv/h-azul.svg"), height=50, width=200)],
        height=100,
        withBorder=True,
    )
