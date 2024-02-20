import dash_mantine_components as dmc
from dash import Input, Output, State, callback, get_asset_url, html, page_registry
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user, logout_user


def layout_header():
    return dmc.Header(
        dmc.Grid(
            my=0,
            px="0.5rem",
            align="center",
            justify="space-between",
            children=[
                dmc.Col(
                    dmc.Anchor(
                        href="/",
                        children=html.Img(
                            src=get_asset_url("imgs/boopt/boopt_azul.svg"),
                            height=30,
                        ),
                    ),
                    span="content",
                    py=5,
                ),
                dmc.Col(id="comp-usr", span="content", py=0),
            ],
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
        minha_area = dmc.Anchor(
            dmc.Button("Minha área", compact=True, variant="light"),
            href="/dashboard",
            refresh=True,
        )
    else:
        nome = "Olá!"
        opcao = [dmc.MenuItem("Entrar", href="/login")]
        minha_area = None

    paginas = [
        dmc.MenuItem(
            f'{page["title"]} [~{page["path"]}]',
            href=page["path"],
            target="_self",
        )
        for page in page_registry.values()
    ]

    menu = dmc.Menu(
        radius="lg",
        children=[
            dmc.MenuTarget(
                dmc.ActionIcon(
                    DashIconify(
                        icon="fluent:caret-down-20-filled",
                    ),
                    variant="filled",
                    color="theme.colors.primaryColor",
                    size=20,
                )
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
    )

    return dmc.Group([minha_area, menu])


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
