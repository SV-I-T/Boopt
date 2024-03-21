import dash_mantine_components as dmc
from dash import Input, Output, callback, get_asset_url, html
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_usuario import Usuario


def layout_navbar():
    return dmc.Navbar(
        children=[
            dmc.Title(id="titulo-navbar", children="Boopt", weight=800, mb="2rem"),
            html.Div(id="menu-usr"),
            html.Img(
                src=get_asset_url("imgs/boopt/horizontal_branco.svg"),
                height=30,
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
                        dmc.Text(
                            f"{usr.nome} {usr.sobrenome}".upper(),
                            weight=600,
                        ),
                        dmc.Menu(
                            [
                                dmc.MenuTarget(
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon="fluent:chevron-down-32-filled",
                                            width=18,
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
                dmc.Text(f"{usr.cargo}", weight=400),
                html.Div(
                    children=[
                        dmc.NavLink(
                            label=dmc.Text("Início", size=16, weight=700),
                            href="/app/assessment-vendedor",
                            icon=DashIconify(icon="fluent:home-20-filled", width=18),
                            active=True,
                        ),
                        dmc.NavLink(
                            label=dmc.Text("Configurações", size=16, weight=700),
                            href="/app/configuracoes",
                            icon=DashIconify(
                                icon="fluent:settings-20-filled", width=18
                            ),
                        ),
                    ]
                ),
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
