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
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Role, Usuario, checar_perfil

register_page(
    __name__,
    path="/app/admin/assessment-vendedor/edit",
    title="Criar Assessment Vendedor",
)


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM])
def layout(empresa: str = None, id: str = None):
    usr: Usuario = current_user

    data_empresas = (
        [
            {"value": str(_empresa["_id"]), "label": _empresa["nome"]}
            for _empresa in usr.buscar_empresas()
        ]
        if usr.role != Role.ADM
        else [str(usr.empresa)]
    )

    if id:
        assessment = AssessmentVendedor(
            **db("AssessmentVendedores", "Aplicações").find_one({"_id": ObjectId(id)})
        )
        texto_titulo = [assessment.descricao]
    else:
        texto_titulo = [
            "Novo Assessment Vendedor",
        ]
        assessment = None

    return [
        html.H1(texto_titulo, className="titulo-pagina"),
        html.Div(
            className="editar-assessment",
            children=[
                dmc.Select(
                    id="empresa-novo-av",
                    icon=DashIconify(icon="fluent:building-24-filled", width=24),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontrei nada",
                    placeholder="Selecione uma empresa",
                    value=str(assessment.empresa)
                    if id
                    else empresa
                    if empresa
                    else str(usr.empresa),
                    w=250,
                    mb="1rem",
                    disabled=bool(id),
                    display="none" if usr.role == Role.ADM else "block",
                ),
                dmc.TextInput(
                    label="Descrição",
                    id="descricao-novo-av",
                    required=True,
                    value=assessment.descricao
                    if id
                    else f'Aplicação - {datetime.now().strftime("%d/%m/%Y")}',
                    mb="1rem",
                ),
                dag.AgGrid(
                    id="usuarios-av",
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
                    rowData=list(
                        db("Boopt", "Usuários").find(
                            {
                                "empresa": ObjectId(
                                    assessment.empresa
                                    if id
                                    else empresa
                                    if empresa
                                    else usr.empresa
                                )
                            },
                            {
                                "_id": 0,
                                "id": {"$toString": "$_id"},
                                "usuario": "$nome",
                                "cargo": 1,
                            },
                        )
                    ),
                    selectedRows=[{"id": str(id)} for id in assessment.participantes]
                    if id
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
                            id="btn-salvar-av" if id else "btn-criar-av",
                            children="Salvar" if id else "Criar",
                            ml="auto",
                            leftIcon=DashIconify(
                                icon="fluent:save-20-regular", width=20
                            ),
                        ),
                        dmc.Button(
                            id="btn-delete-av",
                            children="Excluir",
                            color="red",
                            leftIcon=DashIconify(
                                icon="fluent:delete-20-regular", width=20
                            ),
                        )
                        if id
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


@callback(
    Output("usuarios-av", "rowData"),
    Input("empresa-novo-av", "value"),
    prevent_initial_call=True,
)
def carregar_usuarios_empresa(empresa: str):
    if not empresa:
        raise PreventUpdate

    usuarios = list(
        db("Boopt", "Usuários").find(
            {"empresa": ObjectId(empresa)},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "usuario": {"$concat": ["$nome", " ", "$sobrenome"]},
                "cargo": 1,
            },
        )
    )

    return usuarios


@callback(
    Output("notificacoes", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-criar-av", "n_clicks"),
    State("empresa-novo-av", "value"),
    State("descricao-novo-av", "value"),
    State("usuarios-av", "selectedRows"),
    prevent_initial_call=True,
)
def criar_assessment(n, empresa: str, descricao: str, linhas: list[dict[str, str]]):
    if not n:
        raise PreventUpdate

    usr_atual: Usuario = current_user

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    if not empresa:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Selecione uma empresa",
            action="show",
            color="red",
        ), no_update
    if not descricao:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        ), no_update
    if not linhas:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="red",
        ), no_update

    if (usr_atual.role == Role.ADM) and (usr_atual.empresa != ObjectId(empresa)):
        raise PreventUpdate

    try:
        participantes = [ObjectId(linha["id"]) for linha in linhas]
        nova_aplicacao = AssessmentVendedor(
            empresa=ObjectId(empresa), participantes=participantes, descricao=descricao
        )
        nova_aplicacao.registrar()

    except ValidationError as e:
        erro = e.errors()[0]["ctx"]["error"]
        return dmc.Notification(
            id="notificacao-erro-criacao-av",
            title="Erro",
            message=str(erro),
            action="show",
            color="red",
        ), no_update

    return dmc.Notification(
        id="notificacao-sucesso-criacao-av",
        title="Pronto!",
        message="O Assessment Vendedor foi criado com sucesso",
        action="show",
        color="green",
    ), "/app/admin/assessment-vendedor"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-salvar-av", "n_clicks"),
    State("empresa-novo-av", "value"),
    State("descricao-novo-av", "value"),
    State("usuarios-av", "selectedRows"),
    State("url", "search"),
    prevent_initial_call=True,
)
def atualizar_assessment(
    n: int, empresa: str, descricao: str, linhas: list[dict[str, str]], search: str
):
    if not n:
        raise PreventUpdate

    usr_atual: Usuario = current_user

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate
    if not descricao:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        )
    if not linhas:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="red",
        )

    params = parse_qs(search[1:])
    id_aplicacao = ObjectId(params["id"][0])
    participantes = [ObjectId(linha["id"]) for linha in linhas]

    r = db("AssessmentVendedores", "Aplicações").update_one(
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
            id="notificacao-erro-criacao-av",
            title="Erro",
            message="Ocorreu um erro ao atualizar a aplicação. Tente novamente mais tarde.",
            action="show",
            color="red",
        )

    return dmc.Notification(
        id="notificacao-sucesso-criacao-av",
        title="Pronto!",
        message="O Assessment Vendedor foi atualizado com sucesso",
        action="show",
        color="green",
    )


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("confirm-delete-av", "displayed"),
    Input("btn-delete-av", "n_clicks"),
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

    usr_atual: Usuario = current_user

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    params = parse_qs(search[1:])
    id_aplicacao = ObjectId(params["id"][0])

    aplicacao = db("AssessmentVendedores", "Aplicações").find_one(
        {"_id": id_aplicacao}, {"_id": 0, "empresa": 1}
    )

    if usr_atual.role == Role.ADM and usr_atual.empresa != aplicacao["empresa"]:
        return dmc.Notification(
            id="notificacao-excluir-av",
            title="Atenção",
            message="Você não tem permissão para excluir essa aplicação.",
            action="show",
            color="red",
        ), no_update

    r = db("AssessmentVendedores", "Aplicações").delete_one({"_id": id_aplicacao})

    if not r.acknowledged:
        return dmc.Notification(
            id="notificacao-excluir-av",
            title="Atenção",
            message="Ocorreu um erro ao tentat excluir a aplicação. Tente novamente mais tarde",
            action="show",
            color="red",
        ), no_update

    return dmc.Notification(
        id="notificacao-excluir-av",
        title="Pronto!",
        message="A aplicação foi excluída com sucesso.",
        action="show",
        color="green",
    ), "/app/admin/assessment-vendedor"
