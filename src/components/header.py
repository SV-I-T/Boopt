import dash_mantine_components as dmc
from dash import Input, Output, State, callback, get_asset_url, html, page_registry
from dash.exceptions import PreventUpdate
from flask_login import current_user, logout_user


def layout_header():
    return dmc.Header(
        dmc.Grid(
            [
                dmc.Col(
                    html.Img(src=get_asset_url("imgs/sv/h-azul.svg"), height=50),
                    span="content",
                ),
                dmc.Col(
                    id="comp-usr",
                    span="content",
                ),
                dmc.Col(
                    html.Img(
                        src=get_asset_url("imgs/boopt/HORIZONTAL AZUL.png"), height=50
                    ),
                    span="content",
                ),
            ],
            my=0,
            px="0.5rem",
            align="stretch",
            justify="space-between",
        ),
        height="auto",
        fixed=True,
        withBorder=True,
        id="header",
    )


@callback(
    Output("comp-usr", "children"),
    Input("login-data", "data"),
)
def listar_paginas(_):
    if current_user.is_authenticated:
        nome = f"Olá, {current_user.nome} :)"
        opcao = [
            dmc.MenuItem("Alterar senha", href="/configuracoes/senha"),
            dmc.MenuItem("Sair", id="logout-btn", color="red"),
        ]
    else:
        nome = "Olá!"
        opcao = [dmc.MenuItem("Entrar", href="/login")]

    paginas = [
        dmc.MenuItem(
            f'{page["title"]} [~{page["path"]}]',
            href=page["path"],
            target="_self",
        )
        for page in page_registry.values()
    ]

    menu = (
        dmc.Menu(
            radius="lg",
            children=[
                dmc.MenuTarget(
                    dmc.Button(children=nome, variant="light", compact=True)
                ),
                dmc.MenuDropdown(
                    [
                        dmc.MenuLabel("Minha conta"),
                        *opcao,
                        dmc.MenuDivider(),
                        dmc.MenuLabel("Páginas"),
                        *paginas,
                    ]
                ),
                html.Div(id="logout-timer"),
            ],
        ),
    )
    return menu


@callback(
    Output("logout-timer", "children", allow_duplicate=True),
    Output("login-data", "data", allow_duplicate=True),
    Input("logout-btn", "n_clicks"),
    State("login-data", "data"),
    prevent_initial_call=True,
)
def sair(n, login_data):
    if not n:
        raise PreventUpdate
    logout_user()
    return html.Meta(httpEquiv="refresh", content="0.1"), login_data + 1
