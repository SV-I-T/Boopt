import dash_mantine_components as dmc
from dash import dcc, html, register_page

register_page(__name__, "/admin/usuarios", name="Gerenciamento de usuários")


def layout():
    return [
        dmc.Text("Gerenciamento de usuários", size="xl", weight=700),
        dmc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Usuário"),
                            html.Th("Empresa"),
                            html.Th("Cargo"),
                            html.Th("Ações"),
                        ]
                    )
                )
            ]
        ),
    ]
