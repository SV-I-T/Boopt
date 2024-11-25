import locale

import dash_mantine_components as dmc
from bson import ObjectId
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    clientside_callback,
    dcc,
    html,
    register_page,
)
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

    corpo_tabela = construir_tabela_vela(id_empresa, usr)

    return [
        html.H1(
            [
                dcc.Link("", href="/app/admin", title="Voltar"),
                "Vela Assessment",
            ]
        ),
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
                            id="a-nova-aplicacao",
                            href=f"/app/admin/vela/novo?{('empresa='+empresa) if empresa else ''}",
                            children=dmc.Button(
                                children="Nova aplicação",
                                leftIcon=DashIconify(
                                    icon="fluent:add-20-regular", width=20
                                ),
                            ),
                        )
                        if usr.role != Role.GEST
                        else None,
                        dmc.Anchor(
                            href="/app/admin/vela/dashboard",
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
                                    html.Th("Descrição"),
                                    html.Th("Criado em", style={"width": 120}),
                                    html.Th("Adesão", style={"width": 100}),
                                    html.Th("Nota média", style={"width": 120}),
                                    html.Th("Ações", style={"width": 150}),
                                ]
                            )
                        ),
                        html.Tbody(id="table-vela-body", children=corpo_tabela),
                    ],
                ),
            ]
        ),
    ]


def construir_tabela_vela(empresa: str, usr_atual: Usuario):
    r = db("ViewTabelaVelaAssessments").find({"empresa": ObjectId(empresa)})
    velas = list(r)

    if not velas:
        return [
            html.Tr(
                [html.Td("Sem aplicações", colSpan=5, style={"text-align": "center"})]
            )
        ]

    return [
        html.Tr(
            [
                html.Td(vela.get("descricao", "")),
                html.Td(vela["_id"].generation_time.date().strftime("%d/%m/%Y")),
                html.Td(
                    f'{(vela["respostas"] / vela["participantes"]):.0%} ({vela["respostas"]}/{vela["participantes"]})'
                ),
                html.Td(
                    locale.format_string("%.1f%%", vela["nota_media"] / 70 * 100)
                    if vela["nota_media"]
                    else "--"
                ),
                html.Td(
                    [
                        dmc.Anchor(
                            "Editar",
                            href=f'/app/admin/vela/{vela["_id"]}?empresa={empresa}',
                            mr="0.5rem",
                        )
                        if usr_atual.role != Role.GEST
                        else None,
                        dmc.Anchor(
                            "Respostas",
                            href=f'/app/admin/vela/{vela["_id"]}/view',
                        ),
                    ]
                ),
            ]
        )
        for vela in velas
    ]


clientside_callback(
    ClientsideFunction(namespace="interacoes", function_name="alterar_empresa"),
    Output("url", "search", allow_duplicate=True),
    Input("vela-empresa", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
