import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    clientside_callback,
    get_asset_url,
    html,
)
from dash_iconify import DashIconify
from utils.role import Role
from utils.usuario import Usuario


def layout_navbar():
    usr = Usuario.atual()
    return html.Nav(
        children=[
            dmc.Anchor(
                children=html.Img(
                    src=get_asset_url("imgs/boopt/horizontal_azul.svg"),
                    height=30,
                ),
                href="/app/vela",
            ),
            html.Div(id="menu-usr", children=menu_usuario(usr)),
        ],
        id="navbar",
    )


def menu_usuario(usr: Usuario):
    if usr.is_authenticated:
        return [
            dmc.NavLink(
                label=[
                    dmc.Text(
                        className="nome-usr-navbar",
                        children=usr.primeiro_nome,
                    ),
                    dmc.Text(className="cargo-usr-navbar", children=usr.cargo),
                ],
                icon=DashIconify(icon="fluent:person-20-regular", width=20),
                href="/app/perfil",
            ),
            dmc.NavLink(
                label="Início",
                href="/app/vela",
                icon=DashIconify(icon="fluent:home-20-regular", width=20),
            ),
            dmc.NavLink(
                label="Administração",
                href="/app/admin",
                icon=DashIconify(icon="fluent:shield-person-20-regular", width=20),
            )
            if usr.role in (Role.DEV, Role.ADM)
            else None,
            dmc.NavLink(
                label="Suporte",
                href="/app/support",
                icon=DashIconify(icon="fluent:chat-help-20-regular", width=20),
            ),
            # if usr.role in (Role.DEV, Role.CONST, Role.ADM, Role.GEST)
            # else None,
            dmc.NavLink(
                label="Sair",
                href="/logout",
                icon=DashIconify(icon="fluent:arrow-exit-20-regular", width=20),
                refresh=True,
            ),
        ]

    else:
        return [
            dmc.Text("Você não está logado!"),
            dmc.Anchor("Entrar", href="/login?next=/app/dashboard", refresh=True),
        ]


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="alterar_nav_link"),
    Output("menu-usr", "children"),
    Input("menu-usr", "children"),
)
