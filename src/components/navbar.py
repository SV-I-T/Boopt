import dash_mantine_components as dmc
from dash import Input, Output, State, callback, get_asset_url, html
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_usuario import Perfil, Usuario


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
    Input("navbar", "title"),
    State("url", "pathname"),
)
def menu_usuario(_, path):
    usr: Usuario = current_user

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
                                dmc.Text(
                                    className="empresa-usr-navbar",
                                    children=usr.empresa_nome,
                                ),
                            ],
                            href="/app/perfil",
                            active=path.startswith("/app/perfil"),
                        ),
                        dmc.NavLink(
                            label="Início",
                            href="/app/assessment-vendedor",
                            icon=DashIconify(icon="fluent:home-20-filled", width=18),
                            active=path.startswith("/app/assessment-vendedor"),
                        ),
                        dmc.NavLink(
                            label="Teste",
                            href="/app/assessment-vendedor/teste",
                            icon=DashIconify(
                                icon="fluent:clipboard-text-edit-20-filled", width=18
                            ),
                            active=path.startswith("/app/assessment-vendedor/teste"),
                        ),
                        dmc.NavLink(
                            label="Resultado",
                            href="/app/assessment-vendedor/resultado",
                            icon=DashIconify(
                                icon="fluent:data-treemap-20-filled", width=18
                            ),
                            active=path.startswith(
                                "/app/assessment-vendedor/resultado"
                            ),
                        ),
                        # dmc.NavLink(
                        #     label='Meu perfil',
                        #     href='/app/perfil',
                        #     icon=DashIconify(icon='fluent:person-20-filled', width=18),
                        #     active=path.startswith('/app/perfil')
                        # ),
                        dmc.NavLink(
                            label="Painel de Gestão",
                            href="/app/admin",
                            icon=DashIconify(
                                icon="fluent:panel-left-text-20-filled", width=18
                            ),
                            active=path.startswith("/app/admin"),
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
