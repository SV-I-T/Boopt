import dash_mantine_components as dmc
from dash import register_page, html
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_usuario import Perfil, Usuario, checar_perfil

register_page(__name__, path="/app/admin", title="Painel de gestão")


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout():
    usr: Usuario = current_user

    modulos: tuple[str] = (
        {
            "label": "Usuários",
            "href": "/app/admin/usuarios",
            "icon": "fluent:person-24-filled",
        },
        {
            "label": "Empresas",
            "href": "/app/admin/empresas",
            "icon": "fluent:building-shop-24-filled",
            "perfil": [Perfil.admin, Perfil.dev],
        },
        {
            "label": "Assessment Vendedores",
            "href": "/app/admin/assessment-vendedor",
            "icon": "fluent:checkbox-person-24-filled",
        },
    )
    return [
        html.H1("Painel de gestão", className="titulo-pagina"),
        dmc.Grid(
            children=[
                dmc.Col(
                    xs=6,
                    md=4,
                    children=html.Div(
                        className="card card-painel",
                        children=[
                            dmc.Group(
                                children=[
                                    DashIconify(icon=modulo["icon"], width=24),
                                    dmc.Text(modulo["label"], weight=500),
                                ],
                                align="center",
                            ),
                            dmc.Anchor(
                                href=modulo["href"],
                                underline=False,
                                children=dmc.Button(
                                    "Acessar",
                                    className="btn-borda-gradiente",
                                ),
                            ),
                        ],
                    ),
                )
                for modulo in modulos
                if (usr.perfil in modulo.get("perfil", [usr.perfil]))
            ],
        ),
    ]
