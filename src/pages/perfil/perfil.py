from datetime import datetime

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html, no_update, register_page
from dash.exceptions import PreventUpdate
from flask_login import current_user
from pydantic import ValidationError
from utils.banco_dados import db
from utils.cache import cache_simple
from utils.modelo_usuario import Usuario, checar_perfil
from werkzeug.security import check_password_hash, generate_password_hash

register_page(__name__, path="/app/perfil", title="Meu perfil")


@checar_perfil
def layout():
    usr: Usuario = current_user
    return [
        dmc.Title("Meu perfil", className="titulo-pagina"),
        html.Div(
            className="editar-perfil",
            children=[
                dmc.Title("Informações Pessoais", className="secao-pagina"),
                dmc.SimpleGrid(
                    cols=2,
                    spacing="md",
                    breakpoints=[
                        {"maxWidth": 567, "cols": 1},
                    ],
                    children=[
                        dmc.TextInput(
                            label="Nome completo",
                            value=f"{usr.nome} {usr.sobrenome}",
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
                                        className="btn-link",
                                    ),
                                ],
                            )
                        ),
                        dmc.TextInput(
                            label="Data de nascimento",
                            value=datetime.strptime(usr.data, "%Y-%m-%d").strftime(
                                "%d de %B de %Y"
                            ),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                dmc.Title("Informações Profissionais", className="secao-pagina"),
                dmc.SimpleGrid(
                    cols=2,
                    breakpoints=[
                        {"maxWidth": 567, "co ls": 1},
                    ],
                    children=[
                        dmc.TextInput(
                            label="Empresa",
                            value=db("Boopt", "Empresas").find_one(
                                {"_id": usr.empresa}, {"nome": 1, "_id": 0}
                            )["nome"],
                            disabled=True,
                        ),
                        dmc.TextInput(label="Cargo", value=usr.cargo, disabled=True),
                        dmc.TextInput(
                            label="Perfil",
                            value=usr.perfil.name.capitalize(),
                            disabled=True,
                        ),
                    ],
                ),
                dmc.Divider(),
                dmc.Title("Alteração da senha", className="secao-pagina"),
                dmc.Group(
                    mt="0.5rem",
                    grow=True,
                    align="start",
                    children=[
                        html.Div(
                            [
                                dmc.Text(
                                    "Mantenha sua conta segura alterando a senha padrão",
                                    weight=300,
                                ),
                                dmc.Text(
                                    "ATENÇÃO:",
                                    color="BooptLaranja",
                                    weight=700,
                                    mt="1rem",
                                ),
                                dmc.Text(
                                    "Para alterar sua senha, primeiro você precisa cadastrar um email",
                                    weight=300,
                                ),
                            ]
                        ),
                        dmc.Stack(
                            [
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
                            ]
                        ),
                    ],
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
def habilitar_edicao_email(n: int, acao: str, email: str):
    if not n or not current_user.is_authenticated:
        raise PreventUpdate

    DISABLED_ALTERAR_SENHA = [not bool(email)] * 4

    if acao == "Editar":
        return no_update, False, "Salvar", *DISABLED_ALTERAR_SENHA
    elif acao == "Salvar":
        usr: Usuario = current_user
        try:
            usr.atualizar({"email": email})
        except ValidationError as _:
            return dmc.Notification(
                id="notificacao-email-alterado",
                message="Não conseguimos alterar seu e-mail. Tente novamente mais tarde.",
                color="red",
                title="Atenção",
                action="show",
            ), no_update, no_update, no_update, no_update, no_update, no_update

        cache_simple.delete_memoized(Usuario.buscar_login, Usuario, usr.id)

        return dmc.Notification(
            id="notificacao-email-alterado",
            message="Email alterado com sucesso",
            color="green",
            title="Pronto!",
            action="show",
        ), True, "Editar", *DISABLED_ALTERAR_SENHA
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
    usr: Usuario = current_user
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
