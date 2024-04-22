from math import ceil

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, callback, html, register_page
from dash_iconify import DashIconify
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Perfil, Usuario, checar_perfil
from dash.exceptions import PreventUpdate

register_page(
    __name__, "/app/admin/assessment-vendedor", title="Gerenciar Assessments vendedor"
)

MAX_PAGINA = 10


@checar_perfil(permitir=(Perfil.dev, Perfil.admin, Perfil.gestor))
def layout():
    usr: Usuario = current_user

    if usr.perfil == Perfil.gestor:
        data_empresas = [str(usr.empresa)]
    else:
        data_empresas = [
            {"value": str(empresa["_id"]), "label": empresa["nome"]}
            for empresa in usr.buscar_empresas()
        ]

    corpo_tabela, n_paginas = consultar_dados_tabela_assessment(1, str(usr.empresa))

    return [
        html.H1("Gerenciar Assessment Vendedor", className="titulo-pagina"),
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
                            html.Th("Nota média", style={"width": 120}),
                            html.Th("Ações", style={"width": 150}),
                        ]
                    )
                ),
                html.Tbody(
                    id="tabela-assessment-body",
                    children=corpo_tabela,
                ),
            ],
        ),
        dmc.Pagination(
            id="tabela-assessment-nav", total=n_paginas, page=1, mt="1rem", radius="xl"
        ),
    ]


@callback(
    Output("tabela-assessment-body", "children"),
    Output("tabela-assessment-nav", "total"),
    Output("a-nova-aplicacao", "href"),
    Input("tabela-assessment-nav", "page"),
    Input("empresa-assessment", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_empresas(pagina: int, empresa: str):
    if current_user.perfil not in (Perfil.admin, Perfil.dev, Perfil.gestor):
        raise PreventUpdate
    if current_user.perfil == Perfil.gestor and str(current_user.empresa) != empresa:
        raise PreventUpdate

    corpo_tabela, n_paginas = consultar_dados_tabela_assessment(pagina, empresa)

    return (
        corpo_tabela,
        n_paginas,
        f"/app/admin/assessment-vendedor/edit?empresa={empresa}",
    )


def consultar_dados_tabela_assessment(
    pagina: int, empresa: str
) -> tuple[list[html.Tr], int]:
    r = (
        db("AssessmentVendedores", "Aplicações")
        .aggregate(
            [
                {"$match": {"empresa": ObjectId(empresa)}},
                {"$sort": {"_id": -1}},
                {"$skip": (pagina - 1) * MAX_PAGINA},
                {"$limit": MAX_PAGINA},
                {
                    "$facet": {
                        "cont": [{"$count": "total"}],
                        "data": [
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
                                    "nota_media": {"$avg": "$respostas.nota"},
                                    "respostas": {"$size": "$respostas"},
                                }
                            },
                        ],
                    }
                },
            ]
        )
        .next()
    )

    assessments = r["data"]

    if not assessments:
        return [html.Tr([html.Td("Sem aplicações", colSpan=5)])], 1

    total = r["cont"][0]["total"]

    n_paginas = ceil(total / MAX_PAGINA)

    return [
        html.Tr(
            [
                html.Td(assessment.get("descricao", "")),
                html.Td(assessment["_id"].generation_time.date().strftime("%d/%m/%Y")),
                html.Td(
                    f'{(assessment["respostas"] / assessment["participantes"]):.0%} ({assessment["respostas"]}/{assessment["participantes"]})'
                ),
                html.Td(
                    f'{assessment["nota_media"]:.1f}/70'
                    if assessment["nota_media"]
                    else "--"
                ),
                html.Td(
                    [
                        dmc.Anchor(
                            "Editar",
                            href=f'/app/admin/assessment-vendedor/edit?id={assessment["_id"]}',
                            mr="0.5rem",
                        ),
                        dmc.Anchor(
                            "Resultados",
                            href=f'/app/admin/assessment-vendedor/view?id={assessment["_id"]}',
                        ),
                    ]
                ),
            ]
        )
        for assessment in assessments
    ], n_paginas
