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
from utils.modelo_usuario import Role, Usuario, checar_perfil

register_page(__name__, path="/app/admin/empresas", title="AMD - Empresas")


@checar_perfil(permitir=(Role.DEV))
def layout():
    corpo_tabela = consultar_dados_tabela_empresas("")
    return [
        html.H1("Administração de empresas", className="titulo-pagina"),
        dmc.Group(
            mb="1rem",
            spacing="sm",
            children=[
                dmc.TextInput(
                    id="empresa-filtro-input",
                    placeholder="Pesquisar por nome, segmento...",
                    w=300,
                ),
                dmc.ActionIcon(
                    id="empresa-filtro-btn",
                    children=DashIconify(icon="fluent:search-20-filled", width=24),
                    color="theme.primaryColor",
                    variant="subtle",
                    mr="auto",
                ),
                dmc.Anchor(
                    href="/app/admin/empresas/edit",
                    children=dmc.Button(
                        id="btn-nova-empresa",
                        children="Nova empresa",
                        leftIcon=DashIconify(icon="fluent:add-24-filled", width=24),
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
                            html.Th("Usuários", style={"width": 100}),
                        ]
                    )
                ),
                html.Tbody(id="tabela-empresas-body", children=corpo_tabela),
            ],
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
    empresas = db("Boopt", "Empresas").aggregate(
        [
            {
                "$match": {
                    "$or": [{campo: busca_regex} for campo in ("nome", "segmento")]
                }
            },
            {"$sort": {"nome": 1}},
            {
                "$lookup": {
                    "from": "Usuários",
                    "foreignField": "empresa",
                    "localField": "_id",
                    "as": "usuarios",
                }
            },
            {"$set": {"usuarios": {"$size": "$usuarios"}}},
        ]
    )
    return [
        *[
            html.Tr(
                [
                    html.Td(
                        dmc.Anchor(
                            empresa["nome"],
                            href=f'/app/admin/empresas/edit?id={empresa["_id"]}',
                        )
                    ),
                    html.Td(empresa["segmento"]),
                    html.Td(empresa["usuarios"]),
                ]
            )
            for empresa in empresas
        ],
    ]
