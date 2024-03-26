import dash_mantine_components as dmc
from dash import Input, Output, callback, get_asset_url, html
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_usuario import Usuario


def layout_navbar():
    return html.Nav(
        children=[
            dmc.Text(
                id="titulo-navbar",
                children="Assessment de Vendedores",
                weight=800,
                mb="2rem",
                size=20,
            ),
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
                dmc.Text(
                    className="nome-usr-navbar",
                    children=f"{usr.nome}",
                    weight=600,
                ),
                dmc.Text(className="cargo-usr-navbar", children=usr.cargo, weight=400),
                html.Div(
                    children=[
                        dmc.NavLink(
                            label="Início",
                            href="/app/assessment-vendedor",
                            icon=DashIconify(icon="fluent:home-20-filled", width=18),
                            active=True,
                        ),
                        dmc.NavLink(
                            label="Meu perfil",
                            href="/app/perfil",
                            icon=DashIconify(icon="fluent:person-20-filled", width=18),
                        ),
                        dmc.NavLink(
                            label="Painel de Gestão",
                            href="/app/admin",
                            icon=DashIconify(
                                icon="fluent:panel-left-text-20-filled", width=18
                            ),
                        )
                        if usr.gestor or usr.admin
                        else None,
                        dmc.NavLink(
                            label="Sair",
                            href="/logout",
                            refresh=True,
                            icon=DashIconify(
                                icon="fluent:arrow-exit-20-filled", width=18
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
