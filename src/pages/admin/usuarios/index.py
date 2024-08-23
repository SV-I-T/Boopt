from math import ceil

import dash_mantine_components as dmc
from dash import (
    Input,
    Output,
    State,
    callback,
    callback_context,
    dcc,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils.banco_dados import db
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, "/app/admin/usuarios", name="Usuários")


MAX_PAGINA = 15


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM])
def layout(q: str = "", page: str = "1"):
    page = int(page)

    return [
        html.H1("Usuários", className="titulo-pagina"),
        dmc.Stack(
            [
                dmc.Group(
                    spacing="sm",
                    children=[
                        dmc.TextInput(
                            id="usuario-filtro-input",
                            placeholder="Pesquisar por nome, empresa, cargo...",
                            w=300,
                            value=q,
                        ),
                        dmc.ActionIcon(
                            id="usuario-filtro-btn",
                            children=DashIconify(
                                icon="fluent:search-20-regular", width=24
                            ),
                            color="theme.primaryColor",
                            variant="subtle",
                            mr="auto",
                        ),
                        dmc.Anchor(
                            href="/app/admin/usuarios/new",
                            children=dmc.Button(
                                id="btn-novo-usr",
                                children="Novo Usuário",
                                leftIcon=DashIconify(
                                    icon="fluent:add-24-regular", width=24
                                ),
                                variant="gradient",
                            ),
                        ),
                        dmc.Anchor(
                            href="/app/admin/usuarios/new-batch",
                            children=dmc.Button(
                                id="btn-modal-usr-massa",
                                children="Cadastro em massa",
                            ),
                        ),
                    ],
                ),
                dcc.Store(id="store-request-update-table-users"),
                dmc.Table(
                    striped=True,
                    withColumnBorders=True,
                    withBorder=True,
                    highlightOnHover=True,
                    style={"width": "100%"},
                    children=[
                        html.Thead(
                            html.Tr(
                                [
                                    html.Th("Nome completo", style={"width": 350}),
                                    html.Th("Empresa", style={"width": 200}),
                                    html.Th("Cargo", style={"width": 200}),
                                    html.Th("Perfil", style={"width": 100}),
                                ]
                            )
                        ),
                        html.Tbody(
                            id="tabela-usuarios-body",
                        ),
                    ],
                ),
                dmc.Pagination(
                    id="tabela-usuarios-nav",
                    total=1,
                    page=page,
                    radius="xl",
                ),
            ]
        ),
    ]


@callback(
    Output("tabela-usuarios-body", "children"),
    Output("tabela-usuarios-nav", "total"),
    Output("url-no-refresh", "search"),
    Input("tabela-usuarios-nav", "page"),
    Input("usuario-filtro-btn", "n_clicks"),
    State("usuario-filtro-input", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_usuarios(page: int, n: int, q: str):
    usr_atual = Usuario.atual()
    if usr_atual.role not in [Role.DEV, Role.ADM]:
        raise PreventUpdate

    q = q or ""
    if callback_context.triggered_id != "tabela-usuarios-nav" and n:
        page = 1

    corpo_tabela, total_paginas = consultar_dados_tabela_usuarios(usr_atual, page, q)
    search = "?" + "&".join([f"q={q}", f"page={page}"])

    return corpo_tabela, total_paginas, search


def consultar_dados_tabela_usuarios(
    usr_atual: Usuario, pagina: int, busca: str
) -> tuple[list[html.Tr], int]:
    busca_regex = {"$regex": busca, "$options": "i"}

    pipeline = [
        {
            "$match": {
                "$or": [{campo: busca_regex} for campo in ("nome", "cargo", "empresa")]
            }
        },
        {
            "$facet": {
                "cont": [{"$count": "total"}],
                "usuarios": [
                    {"$skip": (pagina - 1) * MAX_PAGINA},
                    {"$limit": MAX_PAGINA},
                    {"$project": {"id_empresa": 0}},
                ],
            }
        },
    ]

    if usr_atual.role != Role.DEV:
        pipeline.insert(0, {"$match": {"id_empresa": usr_atual.empresa}})

    r = db("ViewTabelaUsuarios").aggregate(pipeline).next()
    usuarios = [Usuario(**usuario) for usuario in r["usuarios"]]
    total = r["cont"][0]["total"] if r["cont"] else 0

    n_paginas = ceil(total / MAX_PAGINA)

    return [
        construir_linha_usuario(usr_atual, usuario) for usuario in usuarios
    ], n_paginas


def construir_linha_usuario(usr_atual: Usuario, usuario: Usuario) -> html.Tr:
    if usr_atual.role == Role.ADM and usuario.role not in [
        Role.usuario,
        Role.candidato,
    ]:
        col_usr = usuario.nome
    else:
        col_usr = dmc.Anchor(
            href=f"/app/admin/usuarios/{usuario.id}",
            children=usuario.nome,
        )
    return html.Tr(
        [
            html.Td(col_usr),
            html.Td(usuario.empresa_nome),
            html.Td(usuario.cargo),
            html.Td(usuario.role),
        ]
    )
