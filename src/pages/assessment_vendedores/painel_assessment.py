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

register_page(__name__, "/assessment-vendedor/painel", title="Painel Assessment")


def carregar_aplicacoes():
    aplicacoes = list(
        db("AssessmentVendedores", "Aplicações").find(
            {}, {"_id": 1, "cliente": 1, "data": 1}
        )
    )
    return aplicacoes


def modal_nova_aplicacao():
    return dmc.Modal(
        id="modal-novo-assessment",
        title=dmc.Title("Nova aplicação", weight=600, order=2),
        zIndex=10000,
    )


def layout():
    aplicacoes = carregar_aplicacoes()
    tabela_aplicacoes = dmc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Link"),
                        html.Th("Cliente"),
                        html.Th("Data"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                dcc.Link(
                                    "Acessar",
                                    href=f'assessment?id={aplicacao.get("_id", "")}',
                                )
                            ),
                            html.Td(str(aplicacao.get("cliente", ""))),
                            html.Td(str(aplicacao.get("data", ""))),
                        ]
                    )
                    for aplicacao in aplicacoes
                ]
            ),
        ]
    )

    return [
        dmc.Title("Aplicações", order=1, weight=700),
        dmc.Button(
            "Nova aplicação",
            id="btn-novo-assessment",
            leftIcon=DashIconify(icon="fluent:add-12-filled", width=24),
            variant="gradient",
        ),
        modal_nova_aplicacao(),
        tabela_aplicacoes,
        dmc.Divider(),
    ]


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="abrir_modal"),
    Output("modal-novo-assessment", "opened"),
    Input("btn-novo-assessment", "n_clicks"),
)
