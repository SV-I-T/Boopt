from typing import Any

import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    html,
    register_page,
)
from dash_iconify import DashIconify

from utils import Missao, Role, Usuario, checar_perfil, db

register_page(__name__, path="/app/admin/missoes", title="Missões de Campo")

MAX_PAGINA = 10


@checar_perfil(permitir=(Role.DEV, Role.CONS))
def layout(empresa: str = None):
    id_empresa = None
    if empresa is not None and len(empresa) == 24:
        id_empresa = empresa

    usr = Usuario.atual()

    data_empresas = usr.consultar_empresas()
    id_empresa = id_empresa or data_empresas[0]["value"]

    n_paginas = 1

    return [
        html.H1("Missões de Campo"),
        dmc.Stack(
            [
                dmc.Group(
                    position="right",
                    children=[
                        dmc.Select(
                            id="missao-empresa",
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
                        ),
                        dmc.Anchor(
                            href=f"/app/admin/missoes/novo?{('empresa='+empresa) if empresa else ''}",
                            children=dmc.Button(
                                children="Nova missão",
                                leftIcon=DashIconify(
                                    icon="fluent:add-20-regular", width=20
                                ),
                            ),
                        ),
                        dmc.Anchor(
                            href="/app/admin/missoes/dashboard",
                            children=dmc.Button(
                                children="Resultados",
                                leftIcon=DashIconify(
                                    icon="fluent:chart-multiple-20-regular", width=20
                                ),
                                color="dark",
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
                                    html.Th("Nome"),
                                    html.Th("Criado em", style={"width": 100}),
                                    html.Th("De", style={"width": 100}),
                                    html.Th("Até", style={"width": 100}),
                                    html.Th("Adesão", style={"width": 100}),
                                    html.Th("Ações", style={"width": 100}),
                                ]
                            )
                        ),
                        html.Tbody(
                            id="table-missoes-body",
                            children=construir_tabela_missoes(id_empresa),
                        ),
                    ],
                ),
                dmc.Pagination(
                    id="table-missoes-nav", total=n_paginas, page=1, radius="xl"
                ),
            ]
        ),
    ]


def construir_tabela_missoes(id_empresa: ObjectId | str):
    if not id_empresa:
        return []
    missoes = [
        Missao(**missao)
        for missao in db("Missões").find(
            {"empresa": ObjectId(id_empresa)}, {"participantes": 0, "campo_desc": 0}
        )
    ]
    missoes_linhas = [
        html.Tr(
            [
                html.Td(missao.nome),
                html.Td(missao.id_.generation_time.strftime("%d/%m/%y")),
                html.Td(missao.dti.strftime("%d/%m/%y")),
                html.Td(missao.dti.strftime("%d/%m/%y")),
                html.Td("0%"),
                html.Td(dmc.Anchor("Editar", href=f"/app/admin/missoes/{missao.id_}")),
            ]
        )
        for missao in reversed(missoes)
    ]
    return missoes_linhas


clientside_callback(
    ClientsideFunction(namespace="interacoes", function_name="alterar_empresa"),
    Output("url", "search", allow_duplicate=True),
    Input("missao-empresa", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
