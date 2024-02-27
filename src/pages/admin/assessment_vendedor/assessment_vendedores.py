from math import ceil

import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    dcc,
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from utils.banco_dados import db

register_page(
    __name__, "/admin/assessment-vendedor", title="Gerenciar Assessments vendedor"
)

MAX_PAGINA = 10


def carregar_aplicacoes():
    aplicacoes = list(
        db("AssessmentVendedores", "Aplicações").find(
            {}, {"_id": 1, "cliente": 1, "data": 1}
        )
    )
    return aplicacoes


def layout():
    n_aplicacoes: int = db("AssessmentVendedores", "Aplicações").count_documents({})
    n_paginas = ceil(n_aplicacoes / MAX_PAGINA)
    return [
        dmc.Title("Gerenciar Assessment Vendedor", order=1, weight=700),
        dmc.Group(
            children=[
                dmc.Anchor(
                    href="/admin/assessment-vendedor/edit",
                    children=dmc.Button(
                        id="btn-nova-aplicacao",
                        children="Nova aplicação",
                        leftIcon=DashIconify(icon="fluent:add-24-filled", width=24),
                        variant="gradient",
                    ),
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
                            html.Th("Empresa", style={"width": 200}),
                            html.Th("Data de criação", style={"width": 200}),
                            html.Th("Participantes", style={"width": 200}),
                            html.Th("Respostas", style={"width": 200}),
                            html.Th("Ações", style={"width": 200}),
                        ]
                    )
                ),
                html.Tbody(id="tabela-assessment-body"),
            ],
        ),
        dmc.Pagination(id="tabela-assessment-nav", total=n_paginas, page=1),
    ]


# @callback(
#     Output("tabela-empresas-body", "children"),
#     Input("url", "pathname"),
#     Input("tabela-empresas-nav", "page"),
#     Input("empresa-filtro-btn", "n_clicks"),
#     State("empresa-filtro-input", "value"),
# )
# def atualizar_tabela_empresas(_, pagina, n, busca):
#     busca_regex = {"$regex": busca, "$options": "i"}
#     empresas = db("Boopt", "Empresas").find(
#         filter={"$or": [{campo: busca_regex} for campo in ("nome", "segmento")]},
#         skip=(pagina - 1) * MAX_PAGINA,
#         limit=MAX_PAGINA,
#         sort={"nome": 1},
#     )
#     return [
#         *[
#             html.Tr(
#                 [
#                     html.Td(str(empresa["_id"])),
#                     html.Td(empresa["nome"]),
#                     html.Td(empresa["segmento"]),
#                     html.Td(
#                         dmc.Anchor(
#                             "Editar", href=f'/admin/empresas/edit?id={empresa["_id"]}'
#                         )
#                     ),
#                 ]
#             )
#             for empresa in empresas
#         ],
#     ]
