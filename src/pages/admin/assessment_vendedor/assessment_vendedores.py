from math import ceil

import dash_mantine_components as dmc
from bson import ObjectId
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
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario, checar_login

register_page(
    __name__, "/app/admin/assessment-vendedor", title="Gerenciar Assessments vendedor"
)

MAX_PAGINA = 10


def carregar_aplicacoes():
    aplicacoes = list(
        db("AssessmentVendedores", "Aplicações").find(
            {}, {"_id": 1, "cliente": 1, "data": 1}
        )
    )
    return aplicacoes


@checar_login(admin=True, gestor=True)
def layout():
    usr_atual: Usuario = current_user

    if usr_atual.admin:
        n_aplicacoes: int = db("AssessmentVendedores", "Aplicações").count_documents({})
    else:
        n_aplicacoes: int = db("AssessmentVendedores", "Aplicações").count_documents(
            {"empresa": usr_atual.empresa}
        )

    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]

    n_paginas = ceil(n_aplicacoes / MAX_PAGINA)
    return [
        dmc.Title("Gerenciar Assessment Vendedor", order=1, weight=700),
        dmc.Group(
            children=[
                dmc.Anchor(
                    href="/app/admin/assessment-vendedor/novo",
                    children=dmc.Button(
                        id="btn-nova-aplicacao",
                        children="Nova aplicação",
                        leftIcon=DashIconify(icon="fluent:add-24-filled", width=24),
                        variant="gradient",
                    ),
                ),
                dmc.Select(
                    id="empresa-assessment",
                    data=data_empresas,
                    searchable=True,
                    nothingFound="Não encontrei nada",
                    placeholder="Selecione uma empresa",
                    w=250,
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
                            html.Th("Data de criação", style={"width": 250}),
                            html.Th("Participantes", style={"width": 150}),
                            html.Th("Respostas", style={"width": 150}),
                            html.Th("Adesão", style={"width": 150}),
                            html.Th("Nota média", style={"width": 150}),
                            html.Th("Acesso", style={"width": 150}),
                        ]
                    )
                ),
                html.Tbody(
                    id="tabela-assessment-body",
                    children=[
                        html.Tr(
                            children=[
                                html.Td(
                                    "Selecione uma empresa primeiro",
                                    colSpan=6,
                                    style={"text-align": "center"},
                                )
                            ]
                        )
                    ],
                ),
            ],
        ),
        dmc.Pagination(id="tabela-assessment-nav", total=n_paginas, page=1),
    ]


@callback(
    Output("tabela-assessment-body", "children"),
    Input("url", "pathname"),
    Input("tabela-assessment-nav", "page"),
    Input("empresa-assessment", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_empresas(_, pagina: int, empresa: str):
    assessments = db("AssessmentVendedores", "Aplicações").aggregate(
        [
            {"$match": {"empresa": ObjectId(empresa)}},
            {"$sort": {"_id": -1}},
            {"$skip": (pagina - 1) * MAX_PAGINA},
            {"$limit": MAX_PAGINA},
            {"$project": {"id_form": 0}},
            {"$set": {"participantes": {"$size": "$participantes"}}},
            {
                "$lookup": {
                    "from": "Respostas",
                    "localField": "_id",
                    "foreignField": "id_aplicacao",
                    "as": "respostas",
                }
            },
            {
                "$set": {
                    "respostas": {"$size": "$respostas"},
                }
            },
        ]
    )
    return [
        *[
            html.Tr(
                [
                    html.Td(
                        assessment["_id"]
                        .generation_time.date()
                        .strftime("%d de %B de %Y")
                    ),
                    html.Td(assessment["participantes"]),
                    html.Td(assessment["respostas"]),
                    html.Td(assessment["respostas"] / assessment["participantes"]),
                    html.Td("50"),
                    html.Td(
                        dmc.Anchor(
                            children="Link de acesso",
                            href=f'/app/assessment-vendedor/teste?id={str(assessment["_id"])}',
                        )
                    ),
                ]
            )
            for assessment in assessments
        ],
    ]