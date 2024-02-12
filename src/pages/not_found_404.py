import dash_mantine_components as dmc
from dash import html, register_page

register_page(__name__, title="Página não encontrada")

layout = [
    dmc.Title(children="Ops!", order=1),
    dmc.Title(children="Parece que essa página não existe.", order=3, weight=500),
    dmc.Anchor(
        children="Clique aqui para voltar à página inicial",
        href="/",
        underline=True,
    ),
]
