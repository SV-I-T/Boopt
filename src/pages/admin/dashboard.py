import dash_mantine_components as dmc
from dash import get_asset_url, html, register_page
from dash_iconify import DashIconify
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, path="/app/admin", title="Painel de gestão")


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout():
    usr = Usuario.atual()
    modules_system = (
        {
            "label": "Empresas",
            "href": "/app/admin/empresas",
            "icon": "fluent:building-48-regular",
            "role": (Role.DEV, Role.CONS),
        },
        {
            "label": "Unidades",
            "href": "/app/admin/unidades",
            "icon": "fluent:building-retail-more-32-regular",
        },
        {
            "label": "Usuários",
            "href": "/app/admin/usuarios",
            "icon": "fluent:person-48-regular",
        },
        {
            "label": "Consultores",
            "href": "/app/admin/consultores",
            "icon": "fluent:person-accounts-24-regular",
            "role": (Role.DEV),
        },
    )
    modules_products = (
        {
            "label": "Vela Assessment",
            "href": "/app/admin/vela",
            "logo": "imgs/vela/tag_ass.svg",
        },
    )

    return [
        html.H1("Gestão", className="titulo-pagina"),
        html.H1("Sistema", className="secao-pagina"),
        html.Div(
            className="grid grid-3-col",
            style={"gap": "1rem"},
            children=[
                dmc.Anchor(
                    href=module["href"],
                    underline=False,
                    children=html.Div(
                        className="card card-painel",
                        children=[
                            dmc.Group(
                                children=[
                                    DashIconify(icon=module["icon"], width=48),
                                    dmc.Text(module["label"], weight=500),
                                ],
                                align="center",
                            ),
                        ],
                    ),
                )
                for module in modules_system
                if (usr.role in module.get("role", [usr.role]))
            ],
        ),
        html.H1("Produtos", className="secao-pagina"),
        html.Div(
            className="grid grid-3-col",
            style={"gap": "1rem"},
            children=[
                dmc.Anchor(
                    href=module["href"],
                    underline=False,
                    children=html.Div(
                        className="card card-painel",
                        children=dmc.Image(src=get_asset_url(module["logo"])),
                    ),
                )
                for module in modules_products
            ],
        ),
    ]