import dash_mantine_components as dmc
from dash import Input, Output, State, callback, get_asset_url, html, page_registry
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario


def layout_navbar():
    return dmc.Navbar(
        children=[
            dmc.Title(
                id="titulo-navbar", children="Boopt", size=40, weight=800, mb="2rem"
            ),
            html.Div(id="menu-usr"),
            dmc.Menu(
                [
                    dmc.MenuTarget(dmc.Button("Páginas", compact=True)),
                    dmc.MenuDropdown(
                        [
                            dmc.MenuItem(
                                f'{page["title"]} [~{page["path"]}]',
                                href=page["path"],
                                target="_self",
                            )
                            for page in page_registry.values()
                        ]
                    ),
                ],
            ),
            dmc.Anchor(
                href="/",
                children=html.Img(
                    src=get_asset_url("imgs/boopt/horizontal_branco.svg"),
                    height=30,
                ),
            ),
        ],
        id="navbar",
    )


@callback(
    Output("menu-usr", "children"),
    Input("login-data", "data"),
)
def menu_usuario(_):
    usr: Usuario = current_user

    if usr.is_authenticated:
        return html.Div(
            children=[
                html.Div(id="logout-timer"),
                dmc.Group(
                    children=[
                        dmc.Anchor(
                            children=dmc.Tooltip(
                                label="Minha área",
                                transition="skew-down",
                                withArrow=True,
                                arrowSize=6,
                                children=dmc.Text(
                                    f"{usr.nome} {usr.sobrenome}".upper(),
                                ),
                            ),
                            weight=600,
                            size=25,
                            href="/app/assessment-vendedor",
                            underline=False,
                            variant="text",
                        ),
                        dmc.Menu(
                            [
                                dmc.MenuTarget(
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon="fluent:chevron-down-32-filled",
                                            width=32,
                                        ),
                                        variant="transparent",
                                    )
                                ),
                                dmc.MenuDropdown(
                                    [
                                        dmc.MenuItem(
                                            "Alterar senha",
                                            href="/app/configuracoes/senha",
                                        ),
                                        dmc.MenuItem(
                                            "Painel de gestão", href="/app/admin"
                                        )
                                        if usr.admin
                                        else None,
                                        dmc.MenuItem(
                                            "Sair",
                                            color="red",
                                            id="logout-btn",
                                            refresh=True,
                                            href="/logout",
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ]
                ),
                dmc.Text(f"{usr.cargo}", size=25, weight=400),
            ]
        )

    else:
        return dmc.Group(
            [
                dmc.Text("Você não está logado!"),
                dmc.Anchor(
                    dmc.Button("Entrar"), href="/login/app/dashboard", refresh=True
                ),
            ]
        )
