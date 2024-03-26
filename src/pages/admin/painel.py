import dash_mantine_components as dmc
from dash import register_page
from dash_iconify import DashIconify
from utils.modelo_usuario import checar_login

register_page(__name__, path="/app/admin", title="Painel de gestão")


@checar_login(admin=True)
def layout():
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
        },
        {
            "label": "Assessment Vendedores",
            "href": "/app/admin/assessment-vendedor",
            "icon": "fluent:checkbox-person-24-filled",
        },
    )
    return [
        dmc.Title("Painel de gestão", order=1, weight=700),
        dmc.Grid(
            children=[
                dmc.Col(
                    xs=6,
                    md=4,
                    children=dmc.Card(
                        shadow="sm",
                        withBorder=True,
                        className="card-painel-gestao",
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
            ],
        ),
    ]
