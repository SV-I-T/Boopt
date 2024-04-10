from datetime import datetime
from urllib.parse import parse_qs

import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Perfil, Usuario, checar_perfil

register_page(
    __name__,
    path="/app/admin/assessment-vendedor/edit",
    title="Criar Assessment Vendedor",
)


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout(empresa: str = None, id: str = None):
    usr: Usuario = current_user

    data_empresas = (
        [
            {"value": str(_empresa["_id"]), "label": _empresa["nome"]}
            for _empresa in usr.buscar_empresas()
        ]
        if usr.perfil != Perfil.gestor
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
        dmc.Title(texto_titulo, className="titulo-pagina"),
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
                    display="none" if usr.perfil == Perfil.gestor else "block",
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
                                "usuario": {"$concat": ["$nome", " ", "$sobrenome"]},
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
                dmc.Button(
                    id="btn-salvar-av" if id else "btn-criar-av",
                    children="Salvar" if id else "Criar",
                    mt="1rem",
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
    Input("btn-criar-av", "n_clicks"),
    State("empresa-novo-av", "value"),
    State("descricao-novo-av", "value"),
    State("usuarios-av", "selectedRows"),
    prevent_initial_call=True,
)
def criar_assessment(n, empresa: str, descricao: str, linhas: list[dict[str, str]]):
    usr: Usuario = current_user
    if (
        not n
        or not usr.is_authenticated
        or (usr.perfil not in [Perfil.admin, Perfil.gestor, Perfil.dev])
    ):
        # Bloqueia se não houve interação ou se o usuário não tem permissão
        raise PreventUpdate

    if not empresa:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Selecione uma empresa",
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
    if not descricao:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        )

    if (usr.perfil == Perfil.gestor) and (usr.empresa != ObjectId(empresa)):
        # Bloqueia se for um gestor e não está criando na própria empresa
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
        )
    else:
        return dmc.Notification(
            id="notificacao-sucesso-criacao-av",
            title="Pronto!",
            message="O Assessment Vendedor foi criado com sucesso",
            action="show",
            color="green",
        )


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
    usr: Usuario = current_user
    if (
        not n
        or not usr.is_authenticated
        or (usr.perfil not in [Perfil.admin, Perfil.gestor, Perfil.dev])
    ):
        # Bloqueia se não houve interação ou se o usuário não tem permissão
        raise PreventUpdate

    if not linhas:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Selecione pelo menos um usuário",
            action="show",
            color="red",
        )
    if not descricao:
        return dmc.Notification(
            id="notificacao-criar-av",
            title="Atenção",
            message="Preencha a descrição da aplicação",
            action="show",
            color="red",
        )

    params = parse_qs(search[1:])

    r = db("AssessmentVendedores", "Aplicações").update_one(
        {"_id": ObjectId(params["id"][0])},
        update={
            "$set": {
                "participantes": [ObjectId(linha["id"]) for linha in linhas],
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
