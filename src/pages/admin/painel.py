import dash_mantine_components as dmc
from dash import register_page
from utils.modelo_usuario import checar_login

register_page(__name__, path="/app/admin", title="Painel de gestão")


@checar_login(admin=True)
def layout():
    modulos: tuple[str] = (
        {"label": "Usuários", "href": "/app/admin/usuarios"},
        {"label": "Empresas", "href": "/app/admin/empresas"},
        {
            "label": "Assessment Vendedores",
            "href": "/app/admin/assessment-vendedor",
        },
    )
    return [
        dmc.Title("Painel de gestão", order=1, weight=700),
        dmc.Grid(
            children=[
                dmc.Col(
                    span="content",
                    children=dmc.Card(
                        shadow="sm",
                        withBorder=True,
                        className="card-painel-gestao",
                        children=[
                            dmc.Text(modulo["label"], weight=500),
                            dmc.Anchor(
                                href=modulo["href"],
                                underline=False,
                                children=dmc.Button(
                                    "Acessar", fullWidth=True, variant="light"
                                ),
                            ),
                        ],
                    ),
                )
                for modulo in modulos
            ],
        ),
    ]
