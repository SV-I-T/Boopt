import locale
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
    html,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils import Role, Usuario, checar_perfil, db

register_page(__name__, "/app/admin/vela", title="Vela Assessment")

MAX_PAGINA = 10


@checar_perfil(permitir=(Role.DEV, Role.ADM, Role.CONS, Role.GEST))
def layout(empresa: str = None):
    id_empresa = None
    if empresa is not None and len(empresa) == 24:
        id_empresa = empresa

    usr = Usuario.atual()

    data_empresas = usr.consultar_empresas()
    id_empresa = id_empresa or data_empresas[0]["value"]

    corpo_tabela, n_paginas = construir_tabela_vela(1, str(usr.empresa), usr)

    return [
        html.H1("Vela Assessment"),
        dmc.Stack(
            [
                dmc.Group(
                    position="right",
                    children=[
                        dmc.Select(
                            id="vela-empresa",
                            icon=DashIconify(
                                icon="fluent:building-20-regular", width=20
                            ),
                            name="empresa",
                            data=data_empresas,
                            required=True,
                            searchable=True,
                            nothingFound="Não encontramos nada",
                            placeholder="Selecione uma empresa",
                            w=250,
                            mr="auto",
                            value=id_empresa,
                            display="none"
                            if usr.role in (Role.ADM, Role.GEST)
                            else "block",
                        ),
                        dmc.Anchor(
                            href="/app/admin/vela/dashboard",
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
                            href=f"/app/admin/vela/novo?{('empresa='+empresa) if empresa else ''}",
                            children=dmc.Button(
                                children="Nova aplicação",
                                leftIcon=DashIconify(
                                    icon="fluent:add-24-regular", width=24
                                ),
                                variant="gradient",
                            ),
                        )
                        if usr.role != Role.GEST
                        else None,
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
                    id="table-vela-nav", total=n_paginas, page=1, radius="xl"
                ),
            ]
        ),
    ]


@callback(
    Output("table-vela-body", "children"),
    Output("table-vela-nav", "total"),
    Input("table-vela-nav", "page"),
    State("vela-empresa", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_empresas(pagina: int, empresa: str):
    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate
    if usr_atual.role == Role.ADM and str(usr_atual.empresa) != empresa:
        raise PreventUpdate

    corpo_tabela, n_paginas = construir_tabela_vela(pagina, empresa, usr_atual)

    return (corpo_tabela, n_paginas)


def construir_tabela_vela(
    pagina: int, empresa: str, usr_atual: Usuario
) -> tuple[list[html.Tr], int]:
    r = (
        db("ViewTabelaVelaAssessments")
        .aggregate(
            [
                {"$match": {"empresa": ObjectId(empresa)}},
                {"$sort": {"_id": -1}},
                {"$skip": (pagina - 1) * MAX_PAGINA},
                {"$limit": MAX_PAGINA},
                {
                    "$facet": {
                        "cont": [{"$count": "total"}],
                        "data": [],
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
                    f'{locale.format_string("%.1f",assessment["nota_media"])}/70'
                    if assessment["nota_media"]
                    else "--"
                ),
                html.Td(
                    [
                        dmc.Anchor(
                            "Editar",
                            href=f'/app/admin/vela/{assessment["_id"]}',
                            mr="0.5rem",
                        )
                        if usr_atual.role != Role.GEST
                        else None,
                        dmc.Anchor(
                            "Respostas",
                            href=f'/app/admin/vela/{assessment["_id"]}/view',
                        ),
                    ]
                ),
            ]
        )
        for assessment in assessments
    ], n_paginas


clientside_callback(
    ClientsideFunction(namespace="interacoes", function_name="alterar_empresa"),
    Output("url", "search", allow_duplicate=True),
    Input("vela-empresa", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
