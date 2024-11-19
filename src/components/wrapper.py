from dash import html, page_container

from components import header


def layout():
    return html.Div(
        id="wrapper",
        children=[
            header.layout(),
            page_container,
        ],
    )
