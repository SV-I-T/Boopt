from datetime import datetime

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
from werkzeug.security import generate_password_hash

from utils import Empresa, Role, UrlUtils, Usuario, checar_perfil, db, nova_notificacao
from utils.login import layout_nao_autorizado
from utils.novo_usuario import NovoUsuario
from utils.usuario import CARGOS_PADROES

register_page(
    __name__, path_template="/app/admin/usuarios/<id_usuario>", title="Editar usuário"
)


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout(id_usuario: str = None):
    usr_atual = Usuario.atual()

    if id_usuario == "novo":
        return [
            html.H1("Novo usuário"),
            *layout_edicao_usr(usr_atual),
        ]

    usr = Usuario.consultar("_id", ObjectId(id_usuario))

    if not autorizado(usr_atual, usr):
        return layout_nao_autorizado()

    return [
        html.H1(
            children=[
                DashIconify(icon="fluent:edit-28-regular", width=28, color="#777"),
                usr.nome,
            ],
            className="titulo-pagina",
        ),
        *layout_edicao_usr(usr_atual, usr),
    ]


def autorizado(usr_atual: Usuario, usr: Usuario) -> bool:
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        return False
    if usr_atual.role == Role.CONS and (usr.empresa not in usr_atual.clientes):
        return False
    if usr_atual.role == Role.ADM and usr.empresa != usr_atual.empresa:
        return False

    return True


def layout_edicao_usr(usr_atual: Usuario, usr: Usuario = None) -> list:
    roles_acessiveis = usr_atual.role.consultar_roles_acessiveis()
    desabilitar_edicao = False if usr is None else usr.role not in roles_acessiveis

    data_perfis = [r.value for r in roles_acessiveis]
    data_empresas = usr_atual.consultar_empresas()
    empresa = Empresa(_id=usr.empresa if usr else usr_atual.empresa)
    data_unidades = [
        {
            "value": unidade.cod,
            "label": f"{unidade.cod}. {unidade.nome}",
        }
        for unidade in empresa.consultar_unidades()
    ]

    return [
        html.H2("Informações Pessoais"),
        html.Div(
            className="grid grid-2-col grid-a-end",
            children=[
                dmc.TextInput(
                    id="nome-edit-usr",
                    label="Nome completo",
                    type="text",
                    icon=DashIconify(icon="fluent:person-20-regular", width=20),
                    name="nome",
                    value=usr.nome if usr else None,
                    disabled=desabilitar_edicao,
                ),
                dmc.TextInput(
                    id="cpf-edit-usr",
                    label="CPF",
                    description="Somente números",
                    placeholder="12345678910",
                    icon=DashIconify(
                        icon="fluent:slide-text-person-20-regular", width=20
                    ),
                    name="cpf",
                    value=usr.cpf if usr else None,
                    disabled=desabilitar_edicao,
                ),
                dmc.TextInput(
                    id="email-edit-usr",
                    label="E-mail (opcional)",
                    type="email",
                    placeholder="nome@dominio.com",
                    icon=DashIconify(icon="fluent:mail-20-regular", width=20),
                    name="email",
                    value=usr.email if usr else None,
                    disabled=desabilitar_edicao,
                ),
                dmc.DatePicker(
                    id="data-edit-usr",
                    label="Data de Nascimento",
                    description="É a senha padrão do usuário",
                    locale="pt-br",
                    inputFormat="DD [de] MMMM [de] YYYY",
                    firstDayOfWeek="sunday",
                    initialLevel="year",
                    clearable=False,
                    placeholder=datetime.now().strftime(r"%d de %B de %Y"),
                    icon=DashIconify(icon="fluent:calendar-20-regular", width=20),
                    name="data",
                    value=usr.data.date() if usr else None,
                    disabled=desabilitar_edicao,
                ),
            ],
        ),
        dmc.Divider(),
        html.H2("Informações Profissionais"),
        html.Div(
            className="grid grid-2-col grid-a-end",
            children=[
                dmc.Select(
                    id="empresa-edit-usr",
                    label="Empresa",
                    icon=DashIconify(icon="fluent:building-20-regular", width=20),
                    name="empresa",
                    data=data_empresas,
                    searchable=True,
                    nothingFound="Não encontramos nada",
                    value=str(usr.empresa if usr else usr_atual.empresa),
                    disabled=desabilitar_edicao or usr_atual.role == Role.ADM,
                ),
                dmc.Select(
                    id="cargo-edit-usr",
                    label="Cargo",
                    description="Selecione a opção mais próxima ou crie uma",
                    data=CARGOS_PADROES,
                    creatable=True,
                    clearable=False,
                    searchable=True,
                    nothingFound="Não encontramos nada",
                    icon=DashIconify(icon="fluent:briefcase-20-regular", width=20),
                    name="cargo",
                    value=usr.cargo if usr else None,
                    disabled=desabilitar_edicao,
                ),
                dmc.MultiSelect(
                    id="unidades-edit-usr",
                    label="Unidade(s)",
                    data=data_unidades,
                    value=usr.unidades if usr else None,
                    disabled=desabilitar_edicao,
                    searchable=True,
                ),
                dmc.Select(
                    id="role-edit-usr",
                    label="Perfil",
                    icon=DashIconify(icon="fluent:person-passkey-20-regular", width=20),
                    data=data_perfis,
                    value=usr.role.value if usr else Role.USR.value,
                    disabled=desabilitar_edicao,
                ),
            ],
        ),
        dmc.Group(
            children=[
                dmc.Button(
                    id="btn-salvar-usr" if usr else "btn-criar-usr",
                    children="Salvar" if usr else "Criar",
                    disabled=desabilitar_edicao,
                    leftIcon=DashIconify(icon="fluent:checkmark-20-regular", width=20),
                ),
                dmc.Button(
                    id="btn-delete-usr",
                    children="Excluir",
                    color="red",
                    disabled=desabilitar_edicao,
                    leftIcon=DashIconify(icon="fluent:delete-20-regular", width=20),
                )
                if usr
                else None,
                dmc.Button(
                    id="btn-reset-usr-password",
                    children="Redefinir senha",
                    disabled=desabilitar_edicao,
                    leftIcon=DashIconify(
                        icon="fluent:arrow-reset-20-regular", width=20
                    ),
                    ml="auto",
                    color="dark",
                )
                if usr
                else None,
            ],
        ),
        dcc.ConfirmDialog(
            id="confirm-reset-usr-password",
            message=f"A senha do usuário {usr.primeiro_nome if usr else None} será redefinida para {usr.data.strftime('%d%m%Y') if usr else None} (Data de aniversário). Tem certeza que deseja redefinir a senha?",
        ),
        dcc.ConfirmDialog(
            id="confirm-delete-usr",
            message=f"Tem certeza que deseja excluir o usuário {usr.nome if usr else None}? Essa ação não pode ser revertida.",
        )
        if usr
        else None,
    ]


@callback(
    Output("unidades-edit-usr", "data"),
    Input("empresa-edit-usr", "value"),
    prevent_initial_call=True,
)
def atualizar_data_unidades(_id_empresa: str):
    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_empresa = ObjectId(_id_empresa)
    if usr_atual.role == Role.ADM and usr_atual.empresa != id_empresa:
        raise PreventUpdate

    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        raise PreventUpdate

    return Empresa.consultar_unidades(id_empresa)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("btn-salvar-usr", "n_clicks"),
    State("nome-edit-usr", "value"),
    State("cpf-edit-usr", "value"),
    State("data-edit-usr", "value"),
    State("email-edit-usr", "value"),
    State("empresa-edit-usr", "value"),
    State("cargo-edit-usr", "value"),
    State("role-edit-usr", "value"),
    State("unidades-edit-usr", "value"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def salvar_usuario(
    n,
    nome: str,
    cpf: str,
    _data: str,
    email: str,
    _empresa: str,
    cargo: str,
    role: str,
    unidades: list[int] | None,
    endpoint: str,
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_usr = UrlUtils.parse_pparams(endpoint, "usuarios")
    data = datetime.strptime(_data, "%Y-%m-%d")
    empresa = ObjectId(_empresa)

    try:
        usr = Usuario.consultar("_id", id_usr)

        if usr_atual.role == Role.ADM:
            if usr_atual.empresa != usr.empresa:
                raise AssertionError(
                    "Você não pode editar um usuário de outra empresa."
                )
            if usr_atual.empresa != empresa:
                raise AssertionError(
                    "Você não pode atribuir outra empresa a um usuário."
                )
            if usr.role not in (Role.GEST, Role.USR, Role.CAND):
                raise AssertionError(
                    "Não você não tem permissão para editar este usuário."
                )
            if role not in (Role.GEST, Role.USR, Role.CAND):
                raise AssertionError(
                    f"Não você não tem permissão para atribuir este perfil: {role.capitalize()}."
                )

        campos = (
            ("nome", usr.nome, nome),
            ("cpf", usr.cpf, cpf),
            ("data", usr.data, data),
            ("email", usr.email, email or None),
            ("empresa", usr.empresa, empresa),
            ("cargo", usr.cargo, cargo or None),
            ("role", usr.role, role),
            ("unidades", usr.unidades, unidades or None),
        )

        campos_alterados = {k: v_novo for k, v, v_novo in campos if v != v_novo}

        usr.atualizar(campos_alterados)

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return nova_notificacao(
            id="feedback-usr",
            type="error",
            message=str(erro),
        ), no_update

    else:
        return nova_notificacao(
            id="feedback-usr",
            type="success",
            message=f"Os dados de {nome} foram atualizados com sucesso.",
        ), "/app/admin/usuarios"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-criar-usr", "n_clicks"),
    State("nome-edit-usr", "value"),
    State("cpf-edit-usr", "value"),
    State("data-edit-usr", "value"),
    State("email-edit-usr", "value"),
    State("empresa-edit-usr", "value"),
    State("cargo-edit-usr", "value"),
    State("role-edit-usr", "value"),
    State("unidades-edit-usr", "value"),
    prevent_initial_call=True,
)
def criar_usuario(
    n: int,
    nome: str,
    cpf: str,
    _data: str,
    email: str,
    _empresa: str,
    cargo: str,
    role: str,
    unidades: list[int] | None,
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    data = datetime.strptime(_data, "%Y-%m-%d")
    empresa = ObjectId(_empresa)

    try:
        if usr_atual.role == Role.ADM:
            if usr_atual.empresa != empresa:
                raise AssertionError(
                    "Não você não pode criar um usuário de outra empresa."
                )
            if role not in (Role.GEST, Role.USR, Role.CAND):
                raise AssertionError(
                    f"Não você não tem permissão para atribuir o perfil '{role.capitalize()}' a alguém."
                )
        usr = NovoUsuario(
            nome=nome,
            cpf=cpf,
            data=data,
            email=email or None,
            empresa=empresa,
            cargo=cargo,
            role=role,
            unidades=unidades or None,
        )
        usr.registrar()

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return nova_notificacao(
            id="notificacao-erro-edit-usr",
            type="error",
            message=str(erro),
        ), no_update

    else:
        return nova_notificacao(
            id="notificacao-novo-usr-suc",
            type="success",
            message=f"O usuário {usr.nome} foi criado com sucesso.",
        ), "/app/admin/usuarios"


clientside_callback(
    ClientsideFunction("interacoes", "ativar"),
    Output("confirm-delete-usr", "displayed"),
    Input("btn-delete-usr", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("confirm-delete-usr", "submit_n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def excluir_usuario(n: int, endpoint: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_usr = UrlUtils.parse_pparams(endpoint, "usuarios")
    filter = {"_id": ObjectId(id_usr)}

    if usr_atual.role == Role.ADM:
        filter["empresa"] = usr_atual.empresa
    elif usr_atual.role == Role.CONS:
        filter["empresa"] = {"$in": usr_atual.clientes}

    r = db("Usuários").delete_one(filter=filter)

    if not r.acknowledged:
        return nova_notificacao(
            id="feedback-usr",
            type="error",
            message="Ocorreu um erro ao tentar excluir o usuário. Tente novamente mais tarde.",
        ), no_update
    elif r.deleted_count == 0:
        return nova_notificacao(
            id="feedback-usr",
            type="error",
            message="Este usuário não existe ou você não tem permissão para excluí-lo.",
        ), no_update

    return nova_notificacao(
        id="feedback-usr",
        type="success",
        message="O usuário foi excluído com sucesso.",
    ), "/app/admin/usuarios"


clientside_callback(
    ClientsideFunction("interacoes", "ativar"),
    Output("confirm-reset-usr-password", "displayed"),
    Input("btn-reset-usr-password", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("confirm-reset-usr-password", "submit_n_clicks"),
    State("url", "pathname"),
    prevent_initial_call=True,
)
def redefinir_senha(n: int, endpoint: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_usr = UrlUtils.parse_pparams(endpoint, "usuarios")
    usr = Usuario.consultar("_id", id_usr)
    nova_senha = usr.data.strftime("%d%m%Y")

    filter = {"_id": ObjectId(id_usr)}
    update = {"$set": {"senha_hash": generate_password_hash(nova_senha)}}

    if usr_atual.role == Role.CONS:
        filter["empresa"] = {"$in": usr_atual.clientes}
    elif usr_atual.role == Role.ADM:
        filter["empresa"] = usr_atual.empresa

    r = db("Usuários").update_one(filter=filter, update=update)

    if not r.acknowledged:
        return nova_notificacao(
            id="feedback-senha",
            type="error",
            message="Houve um erro ao tentar redefinir a senha. Tente novamente mais tarde.",
        )
    elif r.modified_count == 0:
        return nova_notificacao(
            id="feedback-senha",
            type="error",
            message="Este usuário não existe ou você não tem permissao para alterar a senha dele.",
        )

    return nova_notificacao(
        id="feedback-usr",
        type="success",
        message=f"A senha do usuário {usr.nome} foi redefinida com sucesso",
    )
