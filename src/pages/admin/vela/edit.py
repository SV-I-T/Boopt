from datetime import datetime
from urllib.parse import parse_qs

import dash_ag_grid as dag
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
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario
from utils.vela import VelaAssessment

register_page(
    __name__,
    path_template="/app/admin/vela/<id_aplicacao>",
    title="Editar Vela Assessment",
)


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM])
def layout(id_aplicacao: str = None, empresa: str = None, **kwargs):
    usr = Usuario.atual()

    id_aplicacao = None if id_aplicacao == "new" else id_aplicacao

    data_empresas = (
        [
            {"value": str(_empresa["_id"]), "label": _empresa["nome"]}
            for _empresa in usr.buscar_empresas()
        ]
        if usr.role != Role.ADM
        else [str(usr.empresa)]
    )

    if id_aplicacao:
        assessment = carregar_assessment(id_aplicacao=id_aplicacao)
        texto_titulo = [assessment["descricao"]]
    else:
        texto_titulo = [
            "Novo Vela Assessment",
        ]
        assessment = None

    return [
        html.H1(texto_titulo, className="titulo-pagina"),
        html.Div(
            children=[
                dmc.Select(
                    id="empresa-edit-vela",
                    icon=DashIconify(icon="fluent:building-24-regular", width=24),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontrei nada",
                    placeholder="Selecione uma empresa",
                    value=str(assessment["empresa"])
                    if id_aplicacao
                    else empresa
                    if empresa
                    else str(usr.empresa),
                    w=250,
                    mb="1rem",
                    disabled=bool(id_aplicacao),
                    display="none" if usr.role == Role.ADM else "block",
                ),
                dmc.TextInput(
                    label="Descrição",
                    id="desc-edit-vela",
                    required=True,
                    value=assessment["descricao"]
                    if id_aplicacao
                    else f'Vela - {datetime.now().strftime("%d/%m/%Y")}',
                    mb="1rem",
                ),
                dag.AgGrid(
                    id="grid-usrs-vela",
                    columnDefs=[
                        {
                            "field": "id",
                            "hide": True,
                        },
                        {
                            "headerName": "Usuário",
                            "field": "usuario",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "headerCheckboxSelectionFilteredOnly": True,
                        },
                        {"field": "cargo"},
                    ],
                    getRowId="params.data.id",
                    rowData=assessment["usuarios"]
                    if id_aplicacao
                    else carregar_usuarios_empresa(empresa=empresa or usr.empresa),
                    selectedRows=[
                        {"id": usuario["id"]}
                        for usuario in assessment["usuarios"]
                        if usuario["ok"]
                    ]
                    if id_aplicacao
                    else [],
                    dashGridOptions={
                        "rowSelection": "multiple",
                        "suppressRowClickSelection": True,
                        "overlayLoadingTemplate": {
                            "function": "'<span>Selecione uma empresa primeiro</span>'"
                        },
                        "overlayNoRowsTemplate": {
                            "function": "'<span>Não há registros</span>'"
                        },
                    },
                    defaultColDef={
                        "resizable": False,
                        "filter": True,
                        "floatingFilter": True,
                        "floatingFilterComponentParams": {
                            "suppressFilterButton": True,
                        },
                        "suppressMenu": True,
                        "suppressMovable": True,
                        "flex": 1,
                    },
                    className="ag-theme-quartz compact",
                ),
                dmc.Group(
                    mt="1rem",
                    children=[
                        dmc.Button(
                            id="btn-save-vela" if id_aplicacao else "btn-new-vela",
                            children="Salvar" if id_aplicacao else "Criar",
                            ml="auto",
                            leftIcon=DashIconify(
                                icon="fluent:save-20-regular", width=20
                            ),
                        ),
                        dmc.Button(
                            id="btn-delete-vela",
                            children="Excluir",
                            color="red",
                            leftIcon=DashIconify(
                                icon="fluent:delete-20-regular", width=20
                            ),
                        )
                        if id_aplicacao
                        else None,
                        dcc.ConfirmDialog(
                            id="confirm-delete-av",
                            message="Você tem certeza que deseja excluir essa aplicação? Esta ação não poderá ser desfeita.",
                        ),
                    ],
                ),
            ],
        ),
    ]


def carregar_assessment(id_aplicacao: str):
    r = db("VelaAplicações").aggregate(
        [
            {"$match": {"_id": ObjectId(id_aplicacao)}},
            {
                "$lookup": {
                    "from": "Usuários",
                    "let": {"id_empresa": "$empresa"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$empresa", "$$id_empresa"]}}},
                        {
                            "$project": {
                                "_id": 0,
                                "id": "$_id",
                                "usuario": "$nome",
                                "cargo": 1,
                            }
                        },
                    ],
                    "as": "usuarios",
                }
            },
            {
                "$set": {
                    "usuarios": {
                        "$map": {
                            "input": "$usuarios",
                            "in": {
                                "$mergeObjects": [
                                    "$$this",
                                    {
                                        "ok": {"$in": ["$$this.id", "$participantes"]},
                                        "id": {"$toString": "$$this.id"},
                                    },
                                ]
                            },
                        }
                    }
                }
            },
        ]
    )

    if r.alive:
        return r.next()
    return None


def carregar_usuarios_empresa(empresa: str):
    usuarios = list(
        db("Usuários").find(
            {"empresa": ObjectId(empresa)},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "usuario": "$nome",
                "cargo": 1,
            },
        )
    )

    return usuarios


@callback(
    Output("grid-usrs-vela", "rowData"),
    Input("empresa-edit-vela", "value"),
    prevent_initial_call=True,
)
def atualizar_usuarios_empresa(empresa: str):
    if not empresa:
        raise PreventUpdate
    return carregar_usuarios_empresa(empresa)


@callback(
    Output("notificacoes", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-new-vela", "n_clicks"),
    State("empresa-edit-vela", "value"),
    State("desc-edit-vela", "value"),
    State("grid-usrs-vela", "selectedRows"),
    prevent_initial_call=True,
)
def criar_assessment(n, empresa: str, descricao: str, linhas: list[dict[str, str]]):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    if not empresa:
        return dmc.Notification(
            id="notif-new-vela",
            title="Atenção",
            message="Selecione uma empresa",
            action="show",
            color="red",
        ), no_update
    if not descricao:
        return dmc.Notification(
            id="notif-new-vela",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        ), no_update
    if not linhas:
        return dmc.Notification(
            id="notif-new-vela",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="red",
        ), no_update

    if (usr_atual.role == Role.ADM) and (usr_atual.empresa != ObjectId(empresa)):
        raise PreventUpdate

    try:
        participantes = [ObjectId(linha["id"]) for linha in linhas]
        nova_aplicacao = VelaAssessment(
            empresa=ObjectId(empresa), participantes=participantes, descricao=descricao
        )
        nova_aplicacao.registrar()

    except ValidationError as e:
        erro = e.errors()[0]["ctx"]["error"]
        return dmc.Notification(
            id="notif-new-vela",
            title="Erro",
            message=str(erro),
            action="show",
            color="red",
        ), no_update

    return dmc.Notification(
        id="notif-new-vela",
        title="Pronto!",
        message="A aplicação foi criada com sucesso",
        action="show",
        color="green",
    ), "/app/admin/vela"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-save-vela", "n_clicks"),
    State("empresa-edit-vela", "value"),
    State("desc-edit-vela", "value"),
    State("grid-usrs-vela", "selectedRows"),
    State("url", "search"),
    prevent_initial_call=True,
)
def atualizar_assessment(
    n: int, empresa: str, descricao: str, linhas: list[dict[str, str]], search: str
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate
    if not descricao:
        return dmc.Notification(
            id="notif-edit-vela",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        )
    if not linhas:
        return dmc.Notification(
            id="notif-edit-vela",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="red",
        )

    params = parse_qs(search[1:])
    id_aplicacao = ObjectId(params["id"][0])
    participantes = [ObjectId(linha["id"]) for linha in linhas]

    r = db("VelaAplicações").update_one(
        {"_id": id_aplicacao},
        update={
            "$set": {
                "participantes": participantes,
                "descricao": descricao,
            }
        },
    )

    if not r.acknowledged:
        return dmc.Notification(
            id="notif-edit-vela",
            title="Erro",
            message="Ocorreu um erro ao atualizar a aplicação. Tente novamente mais tarde.",
            action="show",
            color="red",
        )

    return dmc.Notification(
        id="notif-edit-vela",
        title="Pronto!",
        message="A aplicação foi atualizada com sucesso",
        action="show",
        color="green",
    )


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("confirm-delete-av", "displayed"),
    Input("btn-delete-vela", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("confirm-delete-av", "submit_n_clicks"),
    State("url", "search"),
    prevent_initial_call=True,
)
def excluir_av(n: int, search: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    params = parse_qs(search[1:])
    id_aplicacao = ObjectId(params["id"][0])

    aplicacao = db("VelaAplicações").find_one(
        {"_id": id_aplicacao}, {"_id": 0, "empresa": 1}
    )

    if usr_atual.role == Role.ADM and usr_atual.empresa != aplicacao["empresa"]:
        return dmc.Notification(
            id="notif-delete-vela",
            title="Atenção",
            message="Você não tem permissão para excluir essa aplicação.",
            action="show",
            color="red",
        ), no_update

    r = db("VelaAplicações").delete_one({"_id": id_aplicacao})

    if not r.acknowledged:
        return dmc.Notification(
            id="notif-delete-vela",
            title="Atenção",
            message="Ocorreu um erro ao tentat excluir a aplicação. Tente novamente mais tarde",
            action="show",
            color="red",
        ), no_update

    return dmc.Notification(
        id="notif-delete-vela",
        title="Pronto!",
        message="A aplicação foi excluída com sucesso.",
        action="show",
        color="green",
    ), "/app/admin/vela"
