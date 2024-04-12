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
from utils.modelo_usuario import Perfil, Usuario, checar_perfil

register_page(__name__, "/app/admin/usuarios", name="Gerenciar usuários")


MAX_PAGINA = 15


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout():
    usr_atual: Usuario = current_user

    if usr_atual.perfil in [Perfil.dev, Perfil.admin]:
        n_usuarios = db("Boopt", "Usuários").count_documents({})
    else:
        n_usuarios = db("Boopt", "Usuários").count_documents(
            {"empresa": usr_atual.empresa}
        )

    n_paginas = ceil(n_usuarios / MAX_PAGINA)
    return [
        dmc.Title("Gerenciar usuários", className="titulo-pagina"),
        dmc.Group(
            mb="1rem",
            spacing="sm",
            children=[
                dmc.TextInput(
                    id="usuario-filtro-input",
                    placeholder="Pesquisar por nome, empresa, cargo...",
                    w=300,
                ),
                dmc.ActionIcon(
                    id="usuario-filtro-btn",
                    children=DashIconify(icon="fluent:search-20-filled", width=24),
                    color="theme.primaryColor",
                    variant="subtle",
                    mr="auto",
                ),
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
                    href="/app/admin/usuarios/cadastro-massa",
                    children=dmc.Button(
                        id="btn-modal-usr-massa",
                        children="Cadastro em massa",
                        variant="light",
                    ),
                ),
            ],
        ),
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
                html.Tbody(id="tabela-usuarios-body"),
            ],
        ),
        dmc.Pagination(
            id="tabela-usuarios-nav", total=n_paginas, page=1, mt="1rem", radius="xl"
        ),
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

    if usr_atual.perfil not in [Perfil.dev, Perfil.admin, Perfil.gestor]:
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
        {
            "$project": {
                campo: 1
                for campo in (
                    "nome",
                    "sobrenome",
                    "cargo",
                    "empresa",
                    "perfil",
                )
            }
        },
    ]

    if usr_atual.perfil not in [Perfil.dev, Perfil.admin]:
        pipeline.insert(0, {"$match": {"empresa": usr_atual.empresa}})

    usuarios = db("Boopt", "Usuários").aggregate(pipeline)
    return [
        *[
            html.Tr(
                [
                    html.Td(
                        [
                            dmc.Anchor(
                                href=f"/app/admin/usuarios/edit?id={usuario['_id']}",
                                children=f'{usuario["nome"]} {usuario["sobrenome"]}',
                            ),
                        ]
                    ),
                    html.Td(usuario.get("empresa", None)),
                    html.Td(usuario.get("cargo", None)),
                    html.Td(Perfil(usuario["perfil"]).name.capitalize()),
                ]
            )
            for usuario in usuarios
        ],
    ]
