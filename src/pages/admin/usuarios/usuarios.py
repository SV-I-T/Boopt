from math import ceil

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
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario, checar_login

register_page(__name__, "/app/admin/usuarios", name="Gerenciar usuários")


MAX_PAGINA = 20


@checar_login(admin=True, gestor=True)
def layout():
    usr_atual: Usuario = current_user

    if usr_atual.admin:
        n_usuarios = db("Boopt", "Usuários").count_documents({})
    else:
        n_usuarios = db("Boopt", "Usuários").count_documents(
            {"empresa": usr_atual.empresa}
        )

    n_paginas = ceil(n_usuarios / MAX_PAGINA)
    return [
        dmc.Title("Gerenciar usuários", order=1, weight=700),
        dmc.Group(
            children=[
                dmc.Anchor(
                    href="/app/admin/usuarios/edit",
                    children=dmc.Button(
                        id="btn-novo-usr",
                        children="Novo Usuário",
                        leftIcon=DashIconify(icon="fluent:add-24-filled", width=24),
                        variant="gradient",
                    ),
                ),
                dmc.Anchor(
                    href="/app/admin/usuarios/batelada",
                    children=dmc.Button(
                        id="btn-modal-usr-massa",
                        children="Cadastro em massa",
                        variant="light",
                    ),
                ),
                dmc.TextInput(
                    id="usuario-filtro-input", placeholder="Pesquisar", w=200
                ),
                dmc.ActionIcon(
                    id="usuario-filtro-btn",
                    children=DashIconify(icon="fluent:search-20-filled", width=20),
                    color="theme.primaryColor",
                    variant="filled",
                ),
            ]
        ),
        dmc.Table(
            striped=True,
            withColumnBorders=True,
            withBorder=True,
            highlightOnHover=True,
            style={"width": "auto"},
            children=[
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Usuário", style={"width": 350}),
                            html.Th("Empresa", style={"width": 200}),
                            html.Th("Cargo", style={"width": 200}),
                            html.Th("Ações", style={"width": 200}),
                        ]
                    )
                ),
                html.Tbody(id="tabela-usuarios-body"),
            ],
        ),
        dmc.Pagination(id="tabela-usuarios-nav", total=n_paginas, page=1),
    ]


@callback(
    Output("tabela-usuarios-body", "children"),
    Input("url", "pathname"),
    Input("tabela-usuarios-nav", "page"),
    Input("usuario-filtro-btn", "n_clicks"),
    State("usuario-filtro-input", "value"),
)
def atualizar_tabela_usuarios(_, pagina: int, n: int, busca: str):
    usr_atual: Usuario = current_user

    if not (usr_atual.gestor or usr_atual.admin):
        raise PreventUpdate

    busca_regex = {"$regex": busca, "$options": "i"}

    pipeline = [
        {"$sort": {"nome": 1}},
        {
            "$lookup": {
                "from": "Empresas",
                "localField": "empresa",
                "foreignField": "_id",
                "as": "empresa",
            }
        },
        {"$set": {"empresa": {"$first": "$empresa.nome"}}},
        {
            "$match": {
                "$or": [
                    {campo: busca_regex}
                    for campo in ("nome", "sobrenome", "cargo", "empresa")
                ]
            }
        },
        {"$skip": (pagina - 1) * MAX_PAGINA},
        {"$limit": MAX_PAGINA},
        {"$project": {campo: 1 for campo in ("nome", "sobrenome", "cargo", "empresa")}},
    ]

    if not usr_atual.admin:
        pipeline.insert(0, {"$match": {"empresa": usr_atual.empresa}})

    usuarios = db("Boopt", "Usuários").aggregate(pipeline)
    return [
        *[
            html.Tr(
                [
                    html.Td(f'{usuario["nome"]} {usuario["sobrenome"]}'),
                    html.Td(usuario.get("empresa", None)),
                    html.Td(usuario["cargo"]),
                    html.Td(
                        dmc.Anchor(
                            "Editar",
                            href=f'/app/admin/usuarios/edit?id={usuario["_id"]}',
                        )
                    ),
                ]
            )
            for usuario in usuarios
        ],
    ]
