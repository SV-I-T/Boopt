import re

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
from flask_login import current_user
from pydantic import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from utils import Role, Usuario, checar_perfil, db, nova_notificacao
from utils.cache import cache_simple

register_page(__name__, path="/app/perfil", title="Meu perfil")


@checar_perfil
def layout():
    usr = Usuario.atual()

    unidades: dict[str, list[str]] = (
        db("Empresas")
        .aggregate(
            [
                {"$match": {"_id": usr.empresa}},
                {
                    "$set": {
                        "unidades": {
                            "$map": {
                                "input": {
                                    "$filter": {
                                        "input": "$unidades",
                                        "as": "unidade",
                                        "cond": {
                                            "$in": ["$$unidade.cod", usr.unidades or []]
                                        },
                                    }
                                },
                                "as": "unidade",
                                "in": "$$unidade.nome",
                            }
                        }
                    }
                },
                {"$project": {"unidades": 1, "_id": 0}},
            ]
        )
        .next()
    )

    return [
        html.H1("Meu perfil"),
        html.Div(
            className="editar-perfil",
            children=[
                html.H2("Informações pessoais"),
                html.Div(
                    className="grid grid-2-col",
                    children=[
                        dmc.TextInput(
                            label="Nome completo",
                            value=f"{usr.nome}",
                            disabled=True,
                        ),
                        dmc.TextInput(label="CPF", value=usr.cpf, disabled=True),
                        dmc.LoadingOverlay(
                            dmc.Group(
                                align="end",
                                spacing="xs",
                                children=[
                                    dmc.TextInput(
                                        label="Email",
                                        value=usr.email,
                                        style={"flex-grow": "1"},
                                        id="input-perfil-email",
                                        disabled=True,
                                    ),
                                    dmc.Button(
                                        "Editar",
                                        id="btn-perfil-editar-email",
                                        mb=8,
                                    ),
                                ],
                            )
                        ),
                        dmc.TextInput(
                            label="Data de nascimento",
                            value=usr.data.strftime("%d de %B de %Y"),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                html.H2("Informações profissionais"),
                html.Div(
                    className="grid grid-2-col",
                    children=[
                        dmc.TextInput(
                            label="Empresa",
                            value=db("Empresas").find_one(
                                {"_id": usr.empresa}, {"nome": 1, "_id": 0}
                            )["nome"],
                            disabled=True,
                        ),
                        dmc.TextInput(label="Cargo", value=usr.cargo, disabled=True),
                        dmc.Textarea(
                            label="Unidade(s)",
                            value=", ".join(unidades["unidades"])
                            or "Sem unidades cadastradas",
                            disabled=True,
                            radius="lg",
                        ),
                        dmc.Textarea(
                            label="Clientes (Apenas Consultores)",
                            value=usr.clientes,
                            disabled=True,
                            display="block"
                            and usr.role in (Role.DEV, Role.CONS)
                            or "none",
                            radius="lg",
                        ),
                        dmc.TextInput(
                            label="Perfil",
                            value=usr.role.value.capitalize(),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                modal_alterar_senha(usr),
                dmc.Button(
                    id="modal-alterar-senha-btn",
                    children="Alterar senha",
                    leftIcon=DashIconify(icon="fluent:open-20-regular", width=20),
                    color="dark",
                ),
                html.Small(
                    "Para alterar sua senha, primeiro você precisa cadastrar um email",
                    style={"margin-left": "1rem"},
                ),
            ],
        ),
    ]


def modal_alterar_senha(usr: Usuario):
    return dmc.Modal(
        title="Alterar senha",
        children=dmc.Stack(
            mb="1rem",
            maw=400,
            children=[
                dmc.PasswordInput(
                    id="input-perfil-senha-atual",
                    label="Senha atual",
                    disabled=not bool(usr.email),
                ),
                dmc.PasswordInput(
                    id="input-perfil-senha-nova",
                    label="Nova senha",
                    disabled=not bool(usr.email),
                ),
                dmc.PasswordInput(
                    id="input-perfil-senha-nova2",
                    label="Confirmação da nova senha",
                    disabled=not bool(usr.email),
                ),
                dmc.Button(
                    id="btn-perfil-alterar-senha",
                    children="Alterar senha",
                    disabled=not bool(usr.email),
                ),
            ],
        ),
        opened=False,
        id="modal-alterar-senha",
    )


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("input-perfil-email", "disabled"),
    Output("btn-perfil-editar-email", "children"),
    Output("input-perfil-senha-atual", "disabled"),
    Output("input-perfil-senha-nova", "disabled"),
    Output("input-perfil-senha-nova2", "disabled"),
    Output("modal-alterar-senha-btn", "disabled"),
    Input("btn-perfil-editar-email", "n_clicks"),
    State("btn-perfil-editar-email", "children"),
    State("input-perfil-email", "value"),
    prevent_initial_call=True,
)
def editar_email(n: int, acao: str, email: str):
    if not n or not current_user.is_authenticated:
        raise PreventUpdate

    DISABLED_ALTERAR_SENHA = [not bool(email)] * 4

    if acao == "Editar":
        return no_update, False, "Salvar", *DISABLED_ALTERAR_SENHA

    elif acao == "Salvar":
        if not re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ).fullmatch(email):
            return (
                nova_notificacao(
                    id="feedback-email",
                    message="E-mail inválido. Verifique e tente novamente",
                    type="error",
                ),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        usr = Usuario.atual()
        try:
            usr.atualizar({"email": email})

        except ValidationError as _:
            return (
                nova_notificacao(
                    id="feedback-email",
                    message="Não conseguimos alterar seu e-mail. Tente novamente mais tarde.",
                    type="error",
                ),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        cache_simple.delete_memoized(Usuario.consultar_pelo_id, Usuario, usr.id)

        return (
            nova_notificacao(
                id="feedback-email",
                message="Email alterado com sucesso",
                type="success",
            ),
            True,
            "Editar",
            *DISABLED_ALTERAR_SENHA,
        )
    else:
        raise PreventUpdate


clientside_callback(
    ClientsideFunction("interacoes", "ativar"),
    Output("modal-alterar-senha", "opened"),
    Input("modal-alterar-senha-btn", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-perfil-alterar-senha", "n_clicks"),
    State("input-perfil-senha-atual", "value"),
    State("input-perfil-senha-nova", "value"),
    State("input-perfil-senha-nova2", "value"),
    prevent_initial_call=True,
)
def alterar_senha(n: int, senha_atual: str, senha_nova: str, senha_nova2: str):
    usr = Usuario.atual()
    if not n or not usr.is_authenticated:
        raise PreventUpdate

    if not senha_atual or not senha_nova or not senha_nova2:
        return nova_notificacao(
            id="notificacao-senha-alterada",
            message="Preencha todos os campos. Tente novamente.",
            type="error",
        )

    if senha_nova != senha_nova2:
        return nova_notificacao(
            id="notificacao-senha-alterada",
            message="As senhas digitadas devem ser iguais. Tente novamente.",
            type="error",
        )

    if not check_password_hash(usr.senha_hash, senha_atual):
        return nova_notificacao(
            id="notificacao-senha-alterada",
            message="Senha atual inválida. Tente novamente.",
            type="error",
        )

    try:
        usr.atualizar({"senha_hash": generate_password_hash(senha_nova)})
    except ValidationError as e:
        return nova_notificacao(
            id="notificacao-senha-alterada",
            message=str(e),
            type="error",
        )

    return nova_notificacao(
        id="notificacao-senha-alterada",
        message="Senha alterada com sucesso",
        type="success",
    )
