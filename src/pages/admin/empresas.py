from math import ceil

import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    html,
    register_page,
)
from dash_iconify import DashIconify
from utils.banco_dados import db
from utils.modelo_usuario import checar_login

register_page(__name__, path="/admin/empresas", title="Gerenciar Empresas")

SEGMENTOS_PADROES = sorted(["Farmácia", "Eletromóveis", "Automóveis", "Imóveis"])
MAX_PAGINA = 20


@checar_login(admin=True)
def layout():
    n_empresas: int = list(db("Boopt", "Empresas").aggregate([{"$count": "nome"}]))[0][
        "nome"
    ]
    n_paginas = ceil(n_empresas / MAX_PAGINA)
    return [
        dmc.Title("Gerenciamento de empresas", order=1, weight=700),
        dmc.Group(
            children=[
                dmc.Button(
                    id="btn-nova-empresa",
                    children="Nova empresa",
                    leftIcon=DashIconify(icon="fluent:add-24-filled", width=24),
                    variant="gradient",
                ),
                dmc.TextInput(
                    id="empresa-filtro-input", placeholder="Pesquisar", w=200
                ),
                dmc.ActionIcon(
                    id="empresa-filtro-btn",
                    children=DashIconify(icon="fluent:search-20-filled", width=20),
                    color="theme.primaryColor",
                    variant="filled",
                ),
            ]
        ),
        dmc.Table(
            striped=True,
            highlightOnHover=True,
            withBorder=True,
            withColumnBorders=True,
            style={"width": "auto"},
            children=[
                html.Thead(
                    html.Tr(
                        [
                            html.Th("ID", style={"width": 200}),
                            html.Th("Nome", style={"width": 200}),
                            html.Th("Segmento", style={"width": 200}),
                            html.Th("Ações", style={"width": 200}),
                        ]
                    )
                ),
                html.Tbody(id="tabela-empresas-body"),
            ],
        ),
        dmc.Pagination(id="tabela-empresas-nav", total=n_paginas, page=1),
    ]


clientside_callback(
    ClientsideFunction("clientside", "redirect_empresas_edit"),
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-nova-empresa", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("tabela-empresas-body", "children"),
    Input("url", "pathname"),
    Input("tabela-empresas-nav", "page"),
    Input("empresa-filtro-btn", "n_clicks"),
    State("empresa-filtro-input", "value"),
)
def atualizar_tabela_empresas(_, pagina, n, busca):
    busca_regex = {"$regex": busca, "$options": "i"}
    empresas = db("Boopt", "Empresas").find(
        filter={"$or": [{campo: busca_regex} for campo in ("nome", "segmento")]},
        skip=(pagina - 1) * MAX_PAGINA,
        limit=MAX_PAGINA,
        sort={"nome": 1},
    )
    return [
        *[
            html.Tr(
                [
                    html.Td(str(empresa["_id"])),
                    html.Td(empresa["nome"]),
                    html.Td(empresa["segmento"]),
                    html.Td(
                        dmc.Anchor(
                            "Editar", href=f'/admin/empresas/edit?id={empresa["_id"]}'
                        )
                    ),
                ]
            )
            for empresa in empresas
        ],
    ]
