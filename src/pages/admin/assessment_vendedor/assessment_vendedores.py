from math import ceil

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, callback, html, register_page
from dash_iconify import DashIconify
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Perfil, Usuario, checar_perfil

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


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout():
    usr: Usuario = current_user

    if usr.perfil in [Perfil.admin, Perfil.dev]:
        n_aplicacoes: int = db("AssessmentVendedores", "Aplicações").count_documents({})
        data_empresas = [
            {"value": str(empresa["_id"]), "label": empresa["nome"]}
            for empresa in usr.buscar_empresas()
        ]
    else:
        n_aplicacoes: int = db("AssessmentVendedores", "Aplicações").count_documents(
            {"empresa": usr.empresa}
        )
        data_empresas = [str(usr.empresa)]

    n_paginas = ceil(n_aplicacoes / MAX_PAGINA)
    return [
        dmc.Title("Gerenciar Assessment Vendedor", className="titulo-pagina"),
        dmc.Group(
            mb="1rem",
            position="right",
            children=[
                dmc.Select(
                    id="empresa-assessment",
                    icon=DashIconify(icon="fluent:building-24-filled", width=24),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontrei nada",
                    placeholder="Selecione uma empresa",
                    w=250,
                    mr="auto",
                    value=str(usr.empresa),
                    display="none" if usr.perfil == Perfil.gestor else "block",
                ),
                dmc.Anchor(
                    id="a-nova-aplicacao",
                    href="/app/admin/assessment-vendedor/edit",
                    children=dmc.Button(
                        id="btn-nova-aplicacao",
                        children="Nova aplicação",
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
                            html.Th("Descrição"),
                            html.Th("Criado em", style={"width": 100}),
                            html.Th("Adesão", style={"width": 100}),
                            html.Th("Ações", style={"width": 100}),
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
        dmc.Pagination(
            id="tabela-assessment-nav", total=n_paginas, page=1, mt="1rem", radius="xl"
        ),
    ]


@callback(
    Output("tabela-assessment-body", "children"),
    Output("a-nova-aplicacao", "href"),
    Input("url", "pathname"),
    Input("tabela-assessment-nav", "page"),
    Input("empresa-assessment", "value"),
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
                    html.Td(assessment.get("descricao", "")),
                    html.Td(
                        assessment["_id"].generation_time.date().strftime("%d/%m/%Y")
                    ),
                    html.Td(
                        f'{(assessment["respostas"] / assessment["participantes"]):.0%} ({assessment["respostas"]}/{assessment["participantes"]})'
                    ),
                    html.Td(
                        [
                            dmc.Anchor(
                                "Editar",
                                href=f'/app/admin/assessment-vendedor/edit?id={assessment["_id"]}',
                                mr="0.5rem",
                            ),
                            dmc.Anchor(
                                "Ver",
                                href=f'/app/admin/assessment-vendedor/view?id={assessment["_id"]}',
                            ),
                        ]
                    ),
                ]
            )
            for assessment in assessments
        ],
    ], f"/app/admin/assessment-vendedor/edit?empresa={empresa}"
