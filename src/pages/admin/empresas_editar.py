from urllib.parse import parse_qs

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from pydantic import ValidationError
from utils.modelo_empresa import Empresa

from .empresas import SEGMENTOS_PADROES

register_page(__name__, path="/admin/empresas/edit", title="Editar empresa")


def layout_nova_empresa(nome: str = None, segmento: str = None):
    return html.Div(
        style={"maxWidth": 300},
        children=[
            dmc.TextInput(
                id="nome-nova-empresa", label="Nome", required=True, value=nome
            ),
            dmc.Select(
                id="segmento-nova-empresa",
                label="Segmento",
                data=SEGMENTOS_PADROES,
                creatable=True,
                searchable=True,
                clearable=True,
                value=segmento,
            ),
            dmc.Button(
                id="btn-criar-nova-empresa" if nome is None else "btn-salvar-empresa",
                children="Criar" if nome is None else "Salvar",
            ),
            html.Div(id="feedback-nova-empresa"),
        ],
    )


def layout(id: str = None):
    if not id:
        texto_titulo = ("Nova Empresa",)
        layout_edicao = layout_nova_empresa()
    else:
        empresa = Empresa.buscar("_id", id)
        texto_titulo = empresa.nome
        layout_edicao = layout_nova_empresa(empresa.nome, empresa.segmento)

    return [
        dmc.Anchor(
            children=dmc.Title("< Gerenciamento de empresas", order=6, weight=500),
            href="/admin/empresas",
            color="dimmed",
            underline=False,
        ),
        dmc.Title(texto_titulo, order=1, weight=700),
        layout_edicao,
    ]


@callback(
    Output("feedback-nova-empresa", "children", allow_duplicate=True),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-criar-nova-empresa", "n_clicks"),
    State("nome-nova-empresa", "value"),
    State("segmento-nova-empresa", "value"),
    prevent_initial_call=True,
)
def criar_empresa(n, nome: str, segmento: str):
    if not n:
        raise PreventUpdate
    try:
        empresa = Empresa(nome=nome, segmento=segmento)
        empresa.registrar()
    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        ALERTA = dmc.Alert(str(erro), color="red", title="Atenção"), no_update
        NOTIFICACAO = no_update
    else:
        ALERTA = no_update
        NOTIFICACAO = dmc.Notification(
            id="empresa-criada",
            color="green",
            title="Pronto!",
            action="show",
            message=[
                dmc.Text("A empresa ", span=True),
                dmc.Text(nome, span=True, weight=700),
                dmc.Text(" foi criada com sucesso.", span=True),
            ],
        )

    return ALERTA, NOTIFICACAO


@callback(
    Output("feedback-nova-empresa", "children", allow_duplicate=True),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-salvar-empresa", "n_clicks"),
    State("nome-nova-empresa", "value"),
    State("segmento-nova-empresa", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
def salvar_empresa(n, nome: str, segmento: str, search: str):
    if not n:
        raise PreventUpdate

    params = parse_qs(search[1:])
    try:
        empresa = Empresa.buscar("_id", params["id"][0])
        empresa.atualizar({"nome": nome, "segmento": segmento})
    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        ALERTA = dmc.Alert(str(erro), color="red"), no_update
        NOTIFICACAO = no_update
    else:
        ALERTA = no_update
        NOTIFICACAO = dmc.Notification(
            id="empresa-salva",
            action="show",
            title="Pronto!",
            message=[
                dmc.Text("A empresa ", span=True),
                dmc.Text(nome, span=True, weight=700),
                dmc.Text(" foi editada com sucesso.", span=True),
            ],
        )
    return ALERTA, NOTIFICACAO