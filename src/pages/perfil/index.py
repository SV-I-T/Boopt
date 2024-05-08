import re

import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.cache import cache_simple
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario
from werkzeug.security import check_password_hash, generate_password_hash

register_page(__name__, path="/app/perfil", title="Meu perfil")


@checar_perfil
def layout():
    usr = Usuario.atual()

    unidades: dict[str, list[str]] = (
        db("Boopt", "Empresas")
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
        html.H1("Meu perfil", className="titulo-pagina"),
        html.Div(
            className="editar-perfil",
            children=[
                html.H1("Informações pessoais", className="secao-pagina"),
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
                html.H1("Informações profissionais", className="secao-pagina"),
                html.Div(
                    className="grid grid-2-col",
                    children=[
                        dmc.TextInput(
                            label="Empresa",
                            value=db("Boopt", "Empresas").find_one(
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
                html.H1("Alterar senha", className="secao-pagina"),
                html.P(
                    "ATENÇÃO:",
                    className="bold c-laranja",
                    style={"margin": 0},
                ),
                html.P(
                    "Para alterar sua senha, primeiro você precisa cadastrar um email",
                    className="light",
                    style={"margin-top": 0},
                ),
                dmc.Stack(
                    mb="1rem",
                    w="50%",
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
                    ],
                ),
                dmc.Button(
                    id="btn-perfil-alterar-senha",
                    children="Alterar senha",
                    disabled=not bool(usr.email),
                ),
            ],
        ),
    ]


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("input-perfil-email", "disabled"),
    Output("btn-perfil-editar-email", "children"),
    Output("input-perfil-senha-atual", "disabled"),
    Output("input-perfil-senha-nova", "disabled"),
    Output("input-perfil-senha-nova2", "disabled"),
    Output("btn-perfil-alterar-senha", "disabled"),
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
                dmc.Notification(
                    id="notificacao-email-alterado",
                    message="E-mail inválido. Verifique e tente novamente",
                    color="red",
                    title="Atenção",
                    action="show",
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
                dmc.Notification(
                    id="notificacao-email-alterado",
                    message="Não conseguimos alterar seu e-mail. Tente novamente mais tarde.",
                    color="red",
                    title="Atenção",
                    action="show",
                ),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        cache_simple.delete_memoized(Usuario.buscar_login, Usuario, usr.id)

        return (
            dmc.Notification(
                id="notificacao-email-alterado",
                message="Email alterado com sucesso",
                color="green",
                title="Pronto!",
                action="show",
            ),
            True,
            "Editar",
            *DISABLED_ALTERAR_SENHA,
        )
    else:
        raise PreventUpdate


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
        return dmc.Notification(
            id="notificacao-senha-alterada",
            message="Preencha todos os campos. Tente novamente.",
            color="red",
            title="Atenção",
            action="show",
        )

    if senha_nova != senha_nova2:
        return dmc.Notification(
            id="notificacao-senha-alterada",
            message="As senhas digitadas devem ser iguais. Tente novamente.",
            color="red",
            title="Atenção",
            action="show",
        )

    if not check_password_hash(usr.senha_hash, senha_atual):
        return dmc.Notification(
            id="notificacao-senha-alterada",
            message="Senha atual inválida. Tente novamente.",
            color="red",
            title="Atenção",
            action="show",
        )

    try:
        usr.atualizar({"senha_hash": generate_password_hash(senha_nova)})
    except ValidationError as e:
        return dmc.Notification(
            id="notificacao-senha-alterada",
            message=str(e),
            color="red",
            title="Atenção",
            action="show",
        )

    return dmc.Notification(
        id="notificacao-senha-alterada",
        message="Senha alterada com sucesso",
        color="green",
        title="Pronto!",
        action="show",
    )
