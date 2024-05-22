from math import ceil

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, callback, html, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from utils.banco_dados import db
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, "/app/admin/vela", title="ADM - Vela Assessment")

MAX_PAGINA = 10


@checar_perfil(permitir=(Role.DEV, Role.ADM))
def layout():
    usr = Usuario.atual()

    if usr.role == Role.ADM:
        data_empresas = [str(usr.empresa)]
    else:
        data_empresas = [
            {"value": str(empresa["_id"]), "label": empresa["nome"]}
            for empresa in usr.buscar_empresas()
        ]

    corpo_tabela, n_paginas = consultar_dados_tabela_vela(1, str(usr.empresa))

    return [
        html.H1("Administração - Vela Assessment", className="titulo-pagina"),
        dmc.Group(
            mb="1rem",
            position="right",
            children=[
                dmc.Select(
                    id="empresa-vela",
                    icon=DashIconify(icon="fluent:building-24-regular", width=24),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontrei nada",
                    placeholder="Selecione uma empresa",
                    w=250,
                    mr="auto",
                    value=str(usr.empresa),
                    display="none" if usr.role == Role.ADM else "block",
                ),
                dmc.Anchor(
                    href="/app/admin/vela/results",
                    children=dmc.Button(
                        children="Resultados",
                        leftIcon=DashIconify(
                            icon="fluent:chart-multiple-24-regular", width=24
                        ),
                        classNames={"root": "btn-vela"},
                    ),
                ),
                dmc.Anchor(
                    id="a-nova-aplicacao",
                    href="/app/admin/vela/edit",
                    children=dmc.Button(
                        children="Nova aplicação",
                        leftIcon=DashIconify(icon="fluent:add-24-regular", width=24),
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
                    id="table-vela-body",
                    children=corpo_tabela,
                ),
            ],
        ),
        dmc.Pagination(
            id="table-vela-nav", total=n_paginas, page=1, mt="1rem", radius="xl"
        ),
    ]


@callback(
    Output("table-vela-body", "children"),
    Output("table-vela-nav", "total"),
    Output("a-nova-aplicacao", "href"),
    Input("table-vela-nav", "page"),
    Input("empresa-vela", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_empresas(pagina: int, empresa: str):
    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate
    if usr_atual.perfil == Role.ADM and str(usr_atual.empresa) != empresa:
        raise PreventUpdate

    corpo_tabela, n_paginas = consultar_dados_tabela_vela(pagina, empresa)

    return (
        corpo_tabela,
        n_paginas,
        f"/app/admin/vela/edit?empresa={empresa}",
    )


def consultar_dados_tabela_vela(pagina: int, empresa: str) -> tuple[list[html.Tr], int]:
    r = (
        db("Boopt", "VelaAplicações")
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
                                    "from": "VelaRespostas",
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
                            href=f'/app/admin/vela/edit?id={assessment["_id"]}',
                            mr="0.5rem",
                        ),
                        dmc.Anchor(
                            "Resultados",
                            href=f'/app/admin/vela/view?id={assessment["_id"]}',
                        ),
                    ]
                ),
            ]
        )
        for assessment in assessments
    ], n_paginas
