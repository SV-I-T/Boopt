import dash_mantine_components as dmc
from dash import (
    Input,
    Output,
    get_asset_url,
    html,
    clientside_callback,
    ClientsideFunction,
)
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_usuario import Perfil, Usuario


def layout_navbar():
    usr: Usuario = current_user
    return html.Nav(
        children=[
            dmc.Text(
                id="titulo-navbar",
                children="Assessment de Vendedores",
                weight=800,
                mb="2rem",
                size=20,
            ),
            html.Div(id="menu-usr", children=menu_usuario(usr)),
            html.Img(
                src=get_asset_url("imgs/boopt/horizontal_branco.svg"),
                height=30,
            ),
        ],
        id="navbar",
    )


def menu_usuario(usr: Usuario):
    if usr.is_authenticated:
        return html.Div(
            children=[
                html.Div(
                    className="links-nav",
                    children=[
                        dmc.NavLink(
                            label=[
                                dmc.Text(
                                    className="nome-usr-navbar",
                                    children=usr.nome,
                                ),
                                dmc.Text(
                                    className="cargo-usr-navbar", children=usr.cargo
                                ),
                            ],
                            icon=DashIconify(icon="fluent:person-20-filled", width=18),
                            href="/app/perfil",
                        ),
                        dmc.NavLink(
                            label="Início",
                            href="/app/assessment-vendedor",
                            icon=DashIconify(icon="fluent:home-20-filled", width=18),
                        ),
                        dmc.NavLink(
                            label="Painel de Gestão",
                            href="/app/admin",
                            icon=DashIconify(
                                icon="fluent:panel-left-text-20-filled", width=18
                            ),
                        )
                        if (usr.perfil in [Perfil.dev, Perfil.admin, Perfil.gestor])
                        else None,
                        dmc.NavLink(
                            label="Sair",
                            href="/logout",
                            icon=DashIconify(
                                icon="fluent:arrow-exit-20-filled", width=18
                            ),
                            refresh=True,
                        ),
                    ],
                ),
            ]
        )

    else:
        return dmc.Group(
            [
                dmc.Text("Você não está logado!"),
                dmc.Anchor("Entrar", href="/login?next=/app/dashboard", refresh=True),
            ]
        )


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="alterar_nav_link"),
    Output("menu-usr", "children"),
    Input("menu-usr", "children"),
)
