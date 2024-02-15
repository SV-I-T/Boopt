from datetime import datetime
from urllib.parse import parse_qs

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from pydantic import ValidationError
from utils.modelo_usuario import NovoUsuario, Usuario

from .usuarios import CARGOS_PADROES

register_page(__name__, path="/admin/usuarios/edit", title="Editar usuário")


def layout_edicao_usr(
    nome: str = None,
    sobrenome: str = None,
    cpf: str = None,
    data: str = None,
    email: str = None,
    cargo: str = None,
    recruta: bool = False,
):
    return html.Div(
        style={"maxWidth": 600},
        children=[
            dmc.Group(
                grow=True,
                children=[
                    dmc.TextInput(
                        id="nome-novo-usr",
                        label="Primeiro Nome",
                        type="text",
                        required=True,
                        icon=DashIconify(icon="fluent:person-24-filled", width=24),
                        name="nome",
                        value=nome,
                    ),
                    dmc.TextInput(
                        id="sobrenome-novo-usr",
                        label="Sobrenome",
                        type="text",
                        required=True,
                        name="sobrenome",
                        value=sobrenome,
                    ),
                ],
            ),
            dmc.Group(
                grow=True,
                children=[
                    dmc.TextInput(
                        id="cpf-novo-usr",
                        label="CPF",
                        type="number",
                        required=True,
                        description="Somente números",
                        placeholder="12345678910",
                        icon=DashIconify(icon="tabler:numbers", width=24),
                        name="cpf",
                        value=cpf,
                    ),
                    dmc.DatePicker(
                        id="data-novo-usr",
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
                        value=datetime.strptime(data, "%Y-%m-%d").date()
                        if data is not None
                        else None,
                    ),
                ],
            ),
            dmc.TextInput(
                id="email-novo-usr",
                label="E-mail",
                type="email",
                description="(Opcional)",
                placeholder="nome@dominio.com",
                icon=DashIconify(icon="fluent:mail-24-filled", width=24),
                name="email",
                value=email,
            ),
            dmc.Select(
                id="cargo-novo-usr",
                label="Cargo/Função",
                required=True,
                description="Selecione a opção que melhor se encaixa ao cargo",
                data=CARGOS_PADROES,
                creatable=True,
                clearable=False,
                searchable=True,
                icon=DashIconify(icon="fluent:person-wrench-20-filled", width=24),
                name="cargo",
                value=cargo,
            ),
            dmc.Checkbox(
                id="recruta-novo-usr", label="Seleção e Recrutamento", checked=recruta
            ),
            dmc.Button(
                id="btn-criar-novo-usr" if nome is None else "btn-salvar-usr",
                children="Criar" if nome is None else "Salvar",
            ),
            html.Div(id="feedback-modal-novo-usr"),
        ],
    )


def layout(id: str = None):
    if not id:
        texto_titulo = "Novo usuário"
        layout_edicao = layout_edicao_usr()
    else:
        usr = Usuario.buscar("_id", ObjectId(id))
        texto_titulo = f"{usr.nome} {usr.sobrenome}"
        layout_edicao = layout_edicao_usr(
            usr.nome,
            usr.sobrenome,
            usr.cpf,
            usr.data,
            usr.email,
            usr.cargo,
            usr.recruta,
        )
    return [
        dmc.Anchor(
            children=dmc.Title("< Usuários", order=6, weight=500),
            href="/admin/usuarios",
            color="dimmed",
            underline=False,
        ),
        dmc.Title(texto_titulo, order=1, weight=700),
        layout_edicao,
    ]


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("feedback-modal-novo-usr", "children"),
    Input("btn-salvar-usr", "n_clicks"),
    State("nome-novo-usr", "value"),
    State("sobrenome-novo-usr", "value"),
    State("cpf-novo-usr", "value"),
    State("data-novo-usr", "value"),
    State("email-novo-usr", "value"),
    State("cargo-novo-usr", "value"),
    State("recruta-novo-usr", "checked"),
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
    cargo: str,
    recruta: bool,
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
                "cargo": cargo,
                "recruta": recruta,
            }
        )
    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        ALERTA = dmc.Alert(str(erro), color="red", title="Atenção")
        NOTIFICACAO = no_update
    else:
        ALERTA = no_update
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

    return NOTIFICACAO, ALERTA


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("feedback-modal-novo-usr", "children", allow_duplicate=True),
    Input("btn-criar-novo-usr", "n_clicks"),
    State("nome-novo-usr", "value"),
    State("sobrenome-novo-usr", "value"),
    State("cpf-novo-usr", "value"),
    State("data-novo-usr", "value"),
    State("email-novo-usr", "value"),
    State("cargo-novo-usr", "value"),
    State("recruta-novo-usr", "checked"),
    prevent_initial_call=True,
)
def criar_novo_usr(
    n,
    nome: str,
    sobrenome: str,
    cpf: str,
    data: str,
    email: str,
    cargo: str,
    recruta: bool,
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
            cargo=cargo,
            recruta=recruta,
        )
        usr.registrar()

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        ALERTA = dmc.Alert(str(erro), color="red", title="Atenção")
        NOTIFICACAO = no_update
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
        ALERTA = no_update

    return NOTIFICACAO, ALERTA
