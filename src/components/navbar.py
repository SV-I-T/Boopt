import dash_mantine_components as dmc
from dash import Input, Output, State, callback, get_asset_url, html
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
    Input("navbar", "title"),
    State("url", "pathname"),
)
def menu_usuario(_, path):
    usr: Usuario = current_user

    if usr.is_authenticated:
        links = [
            {
                "label": "Início",
                "href": "/app/assessment-vendedor",
                "icon": "fluent:home-20-filled",
            },
            {
                "label": "Meu perfil",
                "href": "/app/perfil",
                "icon": "fluent:person-20-filled",
            },
            {
                "label": "Painel de Gestão",
                "href": "/app/admin",
                "icon": "fluent:panel-left-text-20-filled",
                "gestor": True,
            },
            {
                "label": "Sair",
                "href": "/logout",
                "icon": "fluent:arrow-exit-20-filled",
            },
        ]
        return html.Div(
            children=[
                dmc.Text(
                    className="nome-usr-navbar",
                    children=usr.nome,
                ),
                dmc.Text(className="cargo-usr-navbar", children=usr.cargo),
                dmc.Text(
                    className="empresa-usr-navbar",
                    children=usr.empresa_nome,
                ),
                html.Div(
                    className="links-nav",
                    children=[
                        dmc.NavLink(
                            label=link["label"],
                            href=link["href"],
                            icon=DashIconify(icon=link["icon"], width=18),
                            active=path.startswith(link["href"]),
                        )
                        for link in links
                        if ("gestor" not in link)
                        or (link["gestor"] and (usr.gestor or usr.admin))
                    ],
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
