from datetime import datetime
from urllib.parse import parse_qs

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.modelo_usuario import (
    CARGOS_PADROES,
    NovoUsuario,
    Perfil,
    Usuario,
    checar_perfil,
)

register_page(__name__, path="/app/admin/usuarios/edit", title="Editar usuário")


def layout_edicao_usr(usr: Usuario = None):
    usr_atual: Usuario = current_user

    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]

    return html.Div(
        className="editar-usr",
        children=[
            dmc.SimpleGrid(
                cols=2,
                breakpoints=[
                    {"maxWidth": 567, "cols": 1},
                ],
                children=[
                    dmc.TextInput(
                        id="nome-edit-usr",
                        label="Nome",
                        type="text",
                        required=True,
                        icon=DashIconify(icon="fluent:person-24-filled", width=24),
                        name="nome",
                        value=usr.nome if usr else None,
                    ),
                    dmc.TextInput(
                        id="sobrenome-edit-usr",
                        label="Sobrenome",
                        type="text",
                        required=True,
                        name="sobrenome",
                        value=usr.sobrenome if usr else None,
                    ),
                    dmc.TextInput(
                        id="cpf-edit-usr",
                        label="CPF",
                        required=True,
                        description="Somente números",
                        placeholder="12345678910",
                        icon=DashIconify(
                            icon="fluent:slide-text-person-24-filled", width=24
                        ),
                        name="cpf",
                        value=usr.cpf if usr else None,
                    ),
                    dmc.DatePicker(
                        id="data-edit-usr",
                        label="Data de Nascimento",
                        required=True,
                        description="Será a senha do usuário",
                        locale="pt-br",
                        inputFormat="DD [de] MMMM [de] YYYY",
                        firstDayOfWeek="sunday",
                        initialLevel="year",
                        clearable=False,
                        placeholder=datetime.now().strftime(r"%d de %B de %Y"),
                        icon=DashIconify(
                            icon="fluent:calendar-date-24-filled", width=24
                        ),
                        name="data",
                        value=datetime.strptime(usr.data, "%Y-%m-%d").date()
                        if usr
                        else None,
                    ),
                    dmc.TextInput(
                        id="email-edit-usr",
                        label="E-mail",
                        type="email",
                        placeholder="nome@dominio.com",
                        icon=DashIconify(icon="fluent:mail-24-filled", width=24),
                        name="email",
                        value=usr.email if usr else None,
                    ),
                    dmc.Select(
                        id="cargo-edit-usr",
                        label="Cargo/Função",
                        required=True,
                        description="Selecione a opção que melhor se encaixa ao cargo",
                        data=CARGOS_PADROES,
                        creatable=True,
                        clearable=False,
                        searchable=True,
                        icon=DashIconify(
                            icon="fluent:person-wrench-20-filled", width=24
                        ),
                        name="cargo",
                        value=usr.cargo if usr else None,
                    ),
                    dmc.Select(
                        id="empresa-edit-usr",
                        label="Empresa",
                        icon=DashIconify(icon="fluent:building-24-filled", width=24),
                        name="empresa",
                        data=data_empresas,
                        required=True,
                        searchable=True,
                        nothingFound="Não encontrei nada",
                        value=str(usr.empresa) if usr else None,
                    ),
                    dmc.Select(
                        id="perfil-edit-usr",
                        label="Perfil",
                        data=[
                            {"value": p.value, "label": p.name.capitalize()}
                            for p in Perfil
                        ],
                        value=usr.perfil if usr else None,
                    ),
                ],
            ),
            dmc.Button(
                id="btn-salvar-usr" if usr else "btn-criar-usr",
                children="Salvar" if usr else "Criar",
            ),
            dmc.Button(id="btn-excluir-usr", children="Excluir", color="red")
            if usr_atual.perfil in [Perfil.dev, Perfil.admin] and usr is not None
            else None,
        ],
    )


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout(id: str = None):
    if not id:
        texto_titulo = "Novo usuário"
        layout_edicao = layout_edicao_usr()
    else:
        usr = Usuario.buscar("_id", ObjectId(id))
        texto_titulo = [
            DashIconify(icon="fluent:edit-28-filled", width=28, color="#777"),
            f"{usr.nome} {usr.sobrenome}",
        ]
        layout_edicao = layout_edicao_usr(usr)
    return [
        dmc.Title(texto_titulo, className="titulo-pagina"),
        layout_edicao,
    ]


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-salvar-usr", "n_clicks"),
    State("nome-edit-usr", "value"),
    State("sobrenome-edit-usr", "value"),
    State("cpf-edit-usr", "value"),
    State("data-edit-usr", "value"),
    State("email-edit-usr", "value"),
    State("empresa-edit-usr", "value"),
    State("cargo-edit-usr", "value"),
    State("perfil-edit-usr", "value"),
    State("url", "search"),
    prevent_initial_call=True,
)
def salvar_usr(
    n,
    nome: str,
    sobrenome: str,
    cpf: str,
    data: str,
    email: str,
    empresa: str,
    cargo: str,
    perfil: str,
    search: str,
):
    if not n:
        raise PreventUpdate
    params = parse_qs(search[1:])

    try:
        usr = Usuario.buscar("_id", params["id"][0])
        usr.atualizar(
            {
                "nome": nome,
                "sobrenome": sobrenome,
                "cpf": cpf,
                "data": data,
                "email": email,
                "empresa": ObjectId(empresa),
                "cargo": cargo,
                "perfil": perfil,
            }
        )
    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        NOTIFICACAO = dmc.Notification(
            id="notificacao-erro-edit-usr",
            title="Atenção",
            message=str(erro),
            action="show",
            color="red",
        )
    else:
        NOTIFICACAO = dmc.Notification(
            id="notificacao-salvar-usr-suc",
            title="Pronto!",
            message=[
                dmc.Text(span=True, children="O usuário "),
                dmc.Text(span=True, children=nome, weight=700),
                dmc.Text(span=True, children=" foi modificado com sucesso."),
            ],
            color="green",
            action="show",
        )

    return NOTIFICACAO


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-criar-usr", "n_clicks"),
    State("nome-edit-usr", "value"),
    State("sobrenome-edit-usr", "value"),
    State("cpf-edit-usr", "value"),
    State("data-edit-usr", "value"),
    State("email-edit-usr", "value"),
    State("empresa-edit-usr", "value"),
    State("cargo-edit-usr", "value"),
    State("perfil-edit-usr", "value"),
    prevent_initial_call=True,
)
def criar_novo_usr(
    n,
    nome: str,
    sobrenome: str,
    cpf: str,
    data: str,
    email: str,
    empresa: str,
    cargo: str,
    perfil: str,
):
    if not n:
        raise PreventUpdate

    try:
        usr = NovoUsuario(
            nome=nome,
            sobrenome=sobrenome,
            cpf=cpf,
            data=data,
            email=email,
            empresa=empresa,
            cargo=cargo,
            perfil=Perfil(perfil),
        )
        usr.registrar()

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        NOTIFICACAO = NOTIFICACAO = dmc.Notification(
            id="notificacao-erro-edit-usr",
            title="Atenção",
            message=str(erro),
            action="show",
            color="red",
        )
    else:
        NOTIFICACAO = dmc.Notification(
            id="notificacao-novo-usr-suc",
            title="Pronto!",
            message=[
                dmc.Text(span=True, children="O usuário "),
                dmc.Text(span=True, children=nome, weight=700),
                dmc.Text(span=True, children=" foi criado com sucesso."),
            ],
            color="green",
            action="show",
        )

    return NOTIFICACAO


@callback(
    Output("btn-excluir-usr", "children"),
    Output("url", "href"),
    Input("btn-excluir-usr", "n_clicks"),
    State("btn-excluir-usr", "children"),
    State("url", "search"),
    prevent_initial_call=True,
)
def confirmar_exclusao_usr(n: int, botao: str, search: str):
    if not n:
        raise PreventUpdate

    if botao == "Excluir":
        BOTAO = "Confirmar"
        HREF = no_update
    else:
        params = parse_qs(search[1:])
        id = params["id"][0]

        r = db("Boopt", "Usuários").delete_one({"_id": ObjectId(id)})

        BOTAO = no_update
        HREF = "/admin/usuarios"

    return BOTAO, HREF
