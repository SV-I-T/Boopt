import dash_mantine_components as dmc
from dash import html, register_page

register_page(
    __name__,
    path_template="/results/<id_resposta>",
    title="DEMO | Resultados | Vela",
)


def layout(id_resposta: str):
    return [html.Div(style={"margin-top": "7rem"}, children=id_resposta)]
