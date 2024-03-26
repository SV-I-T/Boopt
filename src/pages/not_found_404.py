import dash_mantine_components as dmc
from dash import get_asset_url, html, register_page

register_page(__name__, title="Página não encontrada")

layout = html.Div(
    className="center-container not-found",
    children=[
        dmc.Title(children="OPS...", order=1, weight=600),
        html.Img(src=get_asset_url("imgs/404.png")),
        dmc.Title(children="Parece que essa página não existe.", order=3, weight=400),
        dmc.Anchor(
            children=dmc.Button("Voltar à página inicial"),
            href="/app/dashboard",
            underline=True,
            refresh=True,
        ),
    ],
)
