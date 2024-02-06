import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html, register_page
from dash.exceptions import PreventUpdate
from utils.banco_dados import mongo

register_page(__name__, "/assessment-vendedor/painel", title="Painel Assessment")


def carregar_aplicacoes():
    aplicacoes = list(
        mongo.cx["AssessmentVendedores"]["Aplicações"].find(
            {}, {"_id": 1, "cliente": 1, "data": 1}
        )
    )
    return aplicacoes


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
        dmc.Title("Aplicações", order=3, weight=700),
        tabela_aplicacoes,
        dmc.Divider(),
        dmc.Button("Criar nova aplicação", id="btn-novo-assessment"),
        dmc.Modal(
            id="modal-novo-assessment",
            title="Nova aplicação",
            zIndex=10000,
        ),
    ]


@callback(
    Output("modal-novo-assessment", "opened"),
    Input("btn-novo-assessment", "n_clicks"),
    State("modal-novo-assessment", "opened"),
    prevent_initial_call=True,
)
def abrir_modal_novo_assessment(n, open):
    if not n:
        raise PreventUpdate
    return not open
