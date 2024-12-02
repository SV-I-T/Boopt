from typing import Any

import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from pydantic import ValidationError

from utils import Missao, Role, UrlUtils, Usuario, db, nova_notificacao

register_page(
    __name__,
    path="/app/admin/missoes/novo",
    path_template="/app/admin/missoes/<id_missao>",
)


def layout(id_missao: str, empresa: str = None):
    usr = Usuario.atual()
    novo = id_missao == "novo"

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
        missao = Missao.consultar_missao(id_missao)
    else:
        missao = Missao()

    return [
        html.H1(missao.nome or "Nova missão"),
        dmc.Stack(
            [
                dmc.Select(
                    id="missao-empresa",
                    icon=DashIconify(icon="fluent:building-20-regular", width=20),
                    name="empresa",
                    data=data_empresas,
                    required=True,
                    searchable=True,
                    nothingFound="Não encontramos nada",
                    placeholder="Selecione uma empresa",
                    w=250,
                    mr="auto",
                    value=empresa or str(missao.empresa),
                    disabled=not novo,
                ),
                dmc.Group(
                    grow=True,
                    children=[
                        dmc.TextInput(
                            id="missao-nome",
                            value=missao.nome,
                            required=True,
                            label="Missão",
                        ),
                        dmc.DateRangePicker(
                            id="missao-datas",
                            placeholder="Início - Fim",
                            locale="pt-br",
                            value=[
                                str(missao.dti) if missao.dti else None,
                                str(missao.dtf) if missao.dtf else None,
                            ],
                            inputFormat="DD/MM/YY",
                            firstDayOfWeek="sunday",
                            required=True,
                            label="Prazo",
                        ),
                    ],
                ),
                dmc.TextInput(
                    id="missao-desc",
                    value=missao.descricao,
                    label="Descrição",
                ),
                dmc.TextInput(
                    id="missao-campo-desc",
                    placeholder="Descreva a missão de campo",
                    value=missao.campo_desc,
                    label="Campo de descrição",
                    description="Qual será a pergunta pedindo a descrição da entrega",
                ),
                html.H2("Participantes"),
                dag.AgGrid(
                    id="missao-users",
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
                    selectedRows=[{"id": str(usr)} for usr in missao.participantes],
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
                    dmc.Button(
                        id="missao-salvar",
                        children="Criar" if novo else "Salvar",
                        leftIcon=DashIconify(
                            icon="fluent:checkmark-20-regular", width=20
                        ),
                    )
                ),
            ]
        ),
    ]


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("missao-salvar", "n_clicks"),
    State("missao-nome", "value"),
    State("missao-desc", "value"),
    State("missao-datas", "value"),
    State("missao-campo-desc", "value"),
    State("missao-users", "selectedRows"),
    State("missao-empresa", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def salvar_missao(
    n: int,
    nome: str,
    desc: str,
    datas: list[str, str],
    campo_desc: str,
    users: list[dict[str, Any]],
    empresa: str,
    endpoint: str,
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS):
        raise PreventUpdate

    id_empresa = ObjectId(empresa)
    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        raise PreventUpdate

    try:
        assert nome, "O campo 'Nome' é obrigatório"
        assert all(datas), "O camo 'Prazo' é obrigatório"

        id_users = [ObjectId(user["id"]) for user in users]

        id_missao = UrlUtils.parse_pparams(endpoint, "missoes")
        if id_missao == "novo":
            id_missao = None

        missao = Missao(
            _id=ObjectId(id_missao),
            nome=nome,
            descricao=desc,
            dti=datas[0],
            dtf=datas[1],
            campo_desc=campo_desc,
            participantes=id_users,
            empresa=id_empresa,
        )

        missao.salvar()

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return nova_notificacao(
            id="feedback-missao", type="error", message=str(erro)
        ), no_update

    else:
        return nova_notificacao(
            id="feedback-missao",
            message="A missão foi criada com sucesso.",
            type="success",
        ), "/app/admin/missoes"
