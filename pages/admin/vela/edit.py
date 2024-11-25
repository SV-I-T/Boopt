from datetime import datetime

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

from utils import Role, UrlUtils, Usuario, Vela, checar_perfil, db, nova_notificacao

register_page(
    __name__,
    path="/app/admin/vela/novo",
    path_template="/app/admin/vela/<id_vela>",
    title="Editar Vela Assessment",
)


@checar_perfil(permitir=[Role.DEV, Role.CONS, Role.ADM, Role.GEST])
def layout(id_vela: str = None, empresa: str = None, **kwargs):
    usr = Usuario.atual()
    novo = id_vela == "novo" or len(id_vela) != 24

    if empresa is not None:
        id_empresa = ObjectId(empresa)
    else:
        id_empresa = None

    usuarios = list(
        db("Usuários").find(
            {"empresa": id_empresa},
            {
                "_id": 0,
                "id": {"$toString": "$_id"},
                "usuario": "$nome",
                "cargo": 1,
            },
        )
    )

    data_empresas = usr.consultar_empresas()

    if not novo:
        assessment = Vela.consultar_aplicacao(id_aplicacao=id_vela)
        if assessment is None:
            assessment = Vela()
            novo = True
    else:
        assessment = Vela()

    return [
        html.H1(
            [
                dcc.Link("", href=f"/app/admin/vela?empresa={empresa}", title="Voltar"),
                assessment.descricao or "Novo Vela Assessment",
            ]
        ),
        html.Div(
            children=[
                dmc.Select(
                    id="vela-empresa",
                    icon=DashIconify(icon="fluent:building-20-regular", width=20),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontramos nada",
                    placeholder="Selecione uma empresa",
                    value=empresa or str(assessment.empresa),
                    w=250,
                    mb="1rem",
                    disabled=not novo,
                    display="none" if usr.role == Role.ADM else "block",
                ),
                dmc.TextInput(
                    label="Nome",
                    id="vela-desc",
                    required=True,
                    value=assessment.descricao
                    if not novo
                    else f'Vela - {datetime.now().strftime("%d/%m/%Y")}',
                    mb="1rem",
                ),
                dag.AgGrid(
                    id="vela-users",
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
                    rowData=usuarios,
                    selectedRows=[{"id": str(usr)} for usr in assessment.participantes],
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
                            id="vela-salvar",
                            children="Criar" if novo else "Salvar",
                            leftIcon=DashIconify(
                                icon="fluent:checkmark-20-regular", width=20
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
                        if not novo
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
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("vela-salvar", "n_clicks"),
    State("vela-empresa", "value"),
    State("vela-desc", "value"),
    State("vela-users", "selectedRows"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def atualizar_assessment(
    n: int, empresa: str, descricao: str, users: list[dict[str, str]], endpoint: str
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_empresa = ObjectId(empresa)
    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        raise PreventUpdate

    try:
        assert descricao, "O campo 'Descrição' é obrigatório"
        assert users, "Selecione pelo menos um participante"

        id_users = [ObjectId(user["id"]) for user in users]

        id_aplicacao = UrlUtils.parse_pparams(endpoint, "vela")
        if id_aplicacao == "novo":
            id_aplicacao = None

        assessment = Vela(
            _id=ObjectId(id_aplicacao),
            descricao=descricao,
            empresa=id_empresa,
            participantes=id_users,
        )

        assessment.salvar()

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return nova_notificacao(
            id="feedback-missao",
            type="error",
            message=str(erro),
        ), no_update

    else:
        return nova_notificacao(
            id="feedback-missao",
            type="success",
            message="A missão foi criada com sucesso.",
        ), "/app/admin/vela"


clientside_callback(
    ClientsideFunction("interacoes", "ativar"),
    Output("confirm-delete-av", "displayed"),
    Input("btn-delete-vela", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("confirm-delete-av", "submit_n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def excluir_assessment(n: int, endpoint: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_aplicacao = UrlUtils.parse_pparams(endpoint, "vela")

    aplicacao = db("VelaAplicações").find_one(
        {"_id": ObjectId(id_aplicacao)}, {"_id": 0, "empresa": 1}
    )

    if usr_atual.role == Role.ADM and usr_atual.empresa != aplicacao["empresa"]:
        return nova_notificacao(
            id="notif-delete-vela",
            type="error",
            message="Você não tem permissão para excluir essa aplicação.",
        ), no_update

    r = db("VelaAplicações").delete_one({"_id": ObjectId(id_aplicacao)})

    if not r.acknowledged:
        return nova_notificacao(
            id="notif-delete-vela",
            type="error",
            message="Ocorreu um erro ao tentar excluir a aplicação. Tente novamente mais tarde",
        ), no_update
    elif r.deleted_count == 0:
        return nova_notificacao(
            id="notif-delete-vela",
            type="error",
            message="Essa aplicação não existe mais ou você não tem permissão para excluí-la.",
        ), no_update

    return nova_notificacao(
        id="notif-delete-vela",
        type="success",
        message="A aplicação foi excluída com sucesso.",
    ), "/app/admin/vela"
