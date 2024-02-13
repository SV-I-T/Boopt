import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from pydantic import ValidationError
from utils.modelo_empresa import Empresa
from utils.modelo_usuario import checar_login

register_page(__name__, path="/admin/empresas", title="Gerenciar Empresas")

SEGMENTOS_PADROES = sorted(["Farmácia", "Eletromóveis", "Automóveis", "Imóveis"])


def moval_nova_empresa():
    return dmc.Modal(
        id="modal-nova-empresa",
        title=dmc.Title("Nova Empresa", weight=600, order=2),
        zIndex=10000,
        size=600,
        children=[
            dmc.TextInput(id="nome-nova-empresa", label="Nome", required=True),
            dmc.Select(
                id="segmento-nova-empresa",
                label="Segmento",
                data=SEGMENTOS_PADROES,
                creatable=True,
                searchable=True,
                clearable=True,
            ),
            dmc.Button(id="btn-criar-nova-empresa", children="Criar"),
            html.Div(id="feedback-modal-nova-empresa"),
        ],
    )


@checar_login
def layout():
    return [
        dmc.Title("Gerenciamento de empresas", order=1, weight=700),
        dmc.Button(
            id="btn-modal-nova-empresa",
            children="Nova empresa",
            leftIcon=DashIconify(icon="fluent:add-12-filled", width=24),
            variant="gradient",
        ),
        moval_nova_empresa(),
    ]


clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="abrir_modal"),
    Output("modal-nova-empresa", "opened"),
    Input("btn-modal-nova-empresa", "n_clicks"),
)


@callback(
    Output("modal-nova-empresa", "opened", allow_duplicate=True),
    Output("feedback-modal-nova-empresa", "children"),
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
    except AssertionError as e:
        return no_update, dmc.Alert(str(e), "Atenção!", color="red"), no_update
    except ValidationError as e:
        return no_update, dmc.Alert(
            str(e.errors()[0]["ctx"]["error"]), "Atenção!", color="red"
        ), no_update

    return False, no_update, dmc.Notification(
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
