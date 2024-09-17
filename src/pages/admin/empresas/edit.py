import dash_mantine_components as dmc
from bson import ObjectId
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    dcc,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from pydantic import ValidationError

from utils.banco_dados import db
from utils.empresa import Empresa
from utils.login import checar_perfil
from utils.role import Role
from utils.url import UrlUtils
from utils.usuario import Usuario

register_page(
    __name__, path_template="/app/admin/empresas/<id_empresa>", title="Editar empresa"
)


@checar_perfil(permitir=(Role.DEV, Role.CONS))
def layout(id_empresa: str = None, **kwargs):
    if id_empresa == "new":
        texto_titulo = [
            "Nova Empresa",
        ]
        layout_edicao = layout_nova_empresa()
    else:
        empresa = Empresa.consultar("_id", id_empresa)
        texto_titulo = [
            DashIconify(icon="fluent:edit-28-filled", width=28, color="#777"),
            empresa.nome,
        ]
        layout_edicao = layout_nova_empresa(empresa.nome, empresa.segmento)

    return [
        html.H1(texto_titulo),
        *layout_edicao,
    ]


def layout_nova_empresa(nome: str = None, segmento: str = None):
    segmentos = db("Empresas").distinct("segmento", {"segmento": {"$ne": None}})
    return [
        dmc.TextInput(
            id="nome-nova-empresa", label="Nome", required=True, value=nome, mb="1rem"
        ),
        dmc.Select(
            id="segmento-nova-empresa",
            label="Segmento",
            description="Escolha um dos segmentos existentes ou digite um novo.",
            data=segmentos,
            creatable=True,
            searchable=True,
            clearable=True,
            value=segmento,
            mb="1rem",
        ),
        dmc.Group(
            children=[
                dmc.Button(
                    id="btn-criar-empresa" if nome is None else "btn-salvar-empresa",
                    children="Criar" if nome is None else "Salvar",
                    ml="auto",
                    leftIcon=DashIconify(icon="fluent:save-20-regular", width=20),
                ),
                dmc.Button(
                    id="btn-delete-empresa",
                    children="Excluir",
                    color="red",
                    leftIcon=DashIconify(icon="fluent:delete-20-regular", width=20),
                )
                if nome
                else None,
                dcc.ConfirmDialog(
                    id="confirm-delete-empresa",
                    message=f"Tem certeza que deseja excluir a empresa {nome!r}? Essa ação não pode ser revertida.",
                )
                if nome
                else None,
            ],
        ),
    ]


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("btn-criar-empresa", "n_clicks"),
    State("nome-nova-empresa", "value"),
    State("segmento-nova-empresa", "value"),
    prevent_initial_call=True,
)
def criar_empresa(n, nome: str, segmento: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS):
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
        return dmc.Notification(
            id="notificacao-erro-criar-empresa",
            title="Ops!",
            message=str(erro),
            color="red",
            action="show",
        ), no_update

    else:
        return dmc.Notification(
            id="empresa-criada",
            color="green",
            title="Pronto!",
            action="show",
            message=[
                dmc.Text("A empresa ", span=True),
                dmc.Text(nome, span=True, weight=700),
                dmc.Text(" foi criada com sucesso.", span=True),
            ],
        ), "/app/admin/empresas"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("btn-salvar-empresa", "n_clicks"),
    State("nome-nova-empresa", "value"),
    State("segmento-nova-empresa", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def salvar_empresa(n, nome: str, segmento: str, endpoint: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS):
        raise PreventUpdate

    id_empresa = UrlUtils.parse_pparams(endpoint, "empresas")
    try:
        empresa = Empresa.consultar("_id", id_empresa)
        empresa.atualizar({"nome": nome, "segmento": segmento})

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return dmc.Notification(
            id="notificacao-erro-criar-empresa",
            title="Ops!",
            message=str(erro),
            color="red",
            action="show",
        ), no_update

    else:
        return dmc.Notification(
            id="notificacao-empresa-salva",
            color="green",
            action="show",
            title="Pronto!",
            message=[
                dmc.Text("A empresa ", span=True),
                dmc.Text(nome, span=True, weight=700),
                dmc.Text(" foi editada com sucesso.", span=True),
            ],
        ), "/app/admin/empresas"


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("confirm-delete-empresa", "displayed"),
    Input("btn-delete-empresa", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("confirm-delete-empresa", "submit_n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def excluir_empresa(n: int, endpoint: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS):
        raise PreventUpdate

    id_empresa = UrlUtils.parse_pparams(endpoint, "empresas")

    r = db("Empresas").delete_one({"_id": ObjectId(id_empresa)})

    if not r.acknowledged:
        return dmc.Notification(
            id="notificacao-excluir-usr",
            title="Ops!",
            message="Houve um erro ao excluir a empresa. Tente novamente mais tarde.",
            color="red",
            action="show",
        ), no_update

    return dmc.Notification(
        id="notificacao-excluir-usr",
        title="Pronto!",
        message="A empresa foi excluído com sucesso.",
        color="green",
        action="show",
    ), "/app/admin/empresas"
