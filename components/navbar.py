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


def layout():
    usr = Usuario.atual()
    return html.Nav(
        children=[
            dmc.Anchor(
                children=html.Img(
                    src=get_asset_url("assets/boopt/horizontal_azul.svg")
                ),
                href="/app/vela",
            ),
            html.Div(id="menu-usr", children=menu_usuario(usr)),
            html.Img(src=get_asset_url("assets/sv/tag-h-azul.svg")),
        ],
        id="navbar",
    )


def menu_usuario(usr: Usuario):
    if usr.is_authenticated:
        return [
            dmc.NavLink(
                href="/app/perfil",
                className="usr-card",
                mb="1rem",
                icon=html.Div(children=usr.sigla_nome, className="avatar"),
                label=html.Div(
                    children=[
                        dmc.Text(
                            className="nome-usr-navbar",
                            children=usr.primeiro_nome,
                        ),
                        dmc.Text(className="cargo-usr-navbar", children=usr.cargo),
                    ]
                ),
            ),
            # dmc.NavLink(
            #     label="Minha Boopt",
            #     href="/app/vela",
            #     icon=DashIconify(icon="fluent:home-24-regular", width=24),
            # ),
            dmc.NavLink(
                label="Vela Assessment",
                href="/app/vela",
                icon=html.Span(className="icone-vela"),
            ),
            dmc.NavLink(
                label="Biblioteca de vídeos",
                href="/app/videos/vela",
                icon=DashIconify(icon="fluent:navigation-play-20-regular", width=24),
            ),
            dmc.NavLink(
                label="Gestão",
                href="/app/admin",
                icon=DashIconify(icon="fluent:shield-person-20-regular", width=24),
            )
            if usr.role in (Role.DEV, Role.ADM, Role.CONS, Role.GEST)
            else None,
            dmc.Divider(),
            dmc.NavLink(
                label="Suporte",
                href="/app/support",
                icon=DashIconify(icon="fluent:chat-help-24-regular", width=24),
            ),
            # if usr.role in (Role.DEV, Role.CONST, Role.ADM, Role.GEST)
            # else None,
            dmc.NavLink(
                label="Sair",
                href="/logout",
                icon=DashIconify(icon="fluent:arrow-exit-20-regular", width=24),
                refresh=True,
            ),
        ]

    else:
        return [
            dmc.Text("Você não está logado!"),
            dmc.Anchor("Entrar", href="/login?next=/app/dashboard", refresh=True),
        ]


clientside_callback(
    ClientsideFunction(namespace="interacoes", function_name="alterar_nav_link"),
    Output("menu-usr", "children"),
    Input("menu-usr", "children"),
)
