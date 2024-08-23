import dash_mantine_components as dmc
from dash import (
    Input,
    Output,
    State,
    callback,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils.banco_dados import db
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, path="/app/admin/empresas", title="Empresas")


@checar_perfil(permitir=(Role.DEV))
def layout():
    corpo_tabela = consultar_dados_tabela_empresas("")
    return [
        html.H1("Empresas", className="titulo-pagina"),
        dmc.Stack(
            [
                dmc.Group(
                    spacing="sm",
                    children=[
                        dmc.TextInput(
                            id="empresa-filtro-input",
                            placeholder="Pesquisar por nome, segmento...",
                            w=300,
                        ),
                        dmc.ActionIcon(
                            id="empresa-filtro-btn",
                            children=DashIconify(
                                icon="fluent:search-20-regular", width=24
                            ),
                            color="theme.primaryColor",
                            variant="subtle",
                            mr="auto",
                        ),
                        dmc.Anchor(
                            href="/app/admin/empresas/new",
                            children=dmc.Button(
                                id="btn-nova-empresa",
                                children="Nova empresa",
                                leftIcon=DashIconify(
                                    icon="fluent:add-24-regular", width=24
                                ),
                                variant="gradient",
                            ),
                        ),
                    ],
                ),
                dmc.Table(
                    striped=True,
                    highlightOnHover=True,
                    withBorder=True,
                    withColumnBorders=True,
                    style={"width": "100%"},
                    children=[
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Nome", style={"width": 200}),
                                    html.Th("Segmento", style={"width": 200}),
                                    html.Th("Unidades", style={"width": 100}),
                                    html.Th("Usuários", style={"width": 100}),
                                ]
                            )
                        ),
                        html.Tbody(id="tabela-empresas-body", children=corpo_tabela),
                    ],
                ),
            ]
        ),
    ]


@callback(
    Output("tabela-empresas-body", "children"),
    Input("empresa-filtro-btn", "n_clicks"),
    State("empresa-filtro-input", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_empresas(n: int, busca: str):
    if not n:
        raise PreventUpdate
    usr = Usuario.atual()

    if usr.role not in (Role.DEV, Role.CONS):
        raise PreventUpdate

    corpo_tabela = consultar_dados_tabela_empresas(busca)

    return corpo_tabela


def consultar_dados_tabela_empresas(busca: str):
    busca_regex = {"$regex": busca, "$options": "i"}
    empresas = db("ViewTabelaEmpresas").aggregate(
        [
            {
                "$match": {
                    "$or": [{campo: busca_regex} for campo in ("nome", "segmento")]
                }
            },
        ]
    )
    return [
        *[
            html.Tr(
                [
                    html.Td(
                        dmc.Anchor(
                            empresa["nome"],
                            href=f'/app/admin/empresas/{empresa["_id"]}',
                        )
                    ),
                    html.Td(empresa["segmento"]),
                    html.Td(empresa["unidades"]),
                    html.Td(empresa["usuarios"]),
                ]
            )
            for empresa in empresas
        ],
    ]
