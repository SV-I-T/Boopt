from dash import html, page_container


def layout():
    return html.Div(
        id="wrapper",
        children=[
            html.Div(id="frame"),
            page_container,
            html.Div(id="navbar-backdrop"),
        ],
    )
