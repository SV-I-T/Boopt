import dash_mantine_components as dmc
from dash import html, register_page
from dash_iconify import DashIconify
from utils.modelo_usuario import Role, Usuario, checar_perfil

register_page(__name__, path="/app/admin", title="Painel de administração")


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM])
def layout():
    usr = Usuario.atual()
    modules: tuple[str] = (
        {
            "label": "Usuários",
            "href": "/app/admin/usuarios",
            "icon": "fluent:person-24-filled",
        },
        {
            "label": "Unidades",
            "href": "/app/admin/unidades",
            "icon": "fluent:building-shop-24-filled",
        },
        {
            "label": "Consultores",
            "href": "/app/admin/consultores",
            "icon": "fluent:briefcase-person-24-filled",
            "role": (Role.DEV),
        },
        {
            "label": "Empresas",
            "href": "/app/admin/empresas",
            "icon": "fluent:building-24-filled",
            "role": (Role.DEV, Role.CONS),
        },
        {
            "label": "Vela Assessment",
            "href": "/app/admin/vela",
            "icon": "fluent:checkbox-person-24-filled",
        },
    )
    return [
        html.H1("Painel de administração", className="titulo-pagina"),
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
                                    DashIconify(icon=module["icon"], width=24),
                                    dmc.Text(module["label"], weight=500),
                                ],
                                align="center",
                            ),
                            dmc.Anchor(
                                href=module["href"],
                                underline=False,
                                children=dmc.Button(
                                    "Acessar",
                                    className="btn-borda-gradiente",
                                ),
                            ),
                        ],
                    ),
                )
                for module in modules
                if (usr.role in module.get("role", [usr.role]))
            ],
        ),
    ]
