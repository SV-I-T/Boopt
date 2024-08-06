from datetime import datetime
from urllib.parse import parse_qs

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
from utils.banco_dados import db
from utils.empresa import Empresa
from utils.login import checar_perfil, layout_nao_autorizado
from utils.novo_usuario import NovoUsuario
from utils.role import Role
from utils.usuario import CARGOS_PADROES, Usuario
from werkzeug.security import generate_password_hash

register_page(
    __name__, path_template="/app/admin/usuarios/<id_usuario>", title="Editar usuário"
)


def autorizado(usr_atual: Usuario, usr: Usuario) -> bool:
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        return False
    if usr_atual.role == Role.CONS and (usr.empresa not in usr_atual.clientes):
        return False
    if usr_atual.role == Role.ADM and usr.empresa != usr_atual.empresa:
        return False

    return True


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout(id_usuario: str = None):
    id_usuario = None if id_usuario == "new" else id_usuario

    usr_atual = Usuario.atual()

    if not id_usuario:
        return [
            html.H1("Novo usuário", className="titulo-pagina"),
            layout_edicao_usr(usr_atual),
        ]

    usr = Usuario.buscar("_id", ObjectId(id_usuario))

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
        layout_edicao_usr(usr_atual, usr),
    ]


def layout_edicao_usr(usr_atual: Usuario, usr: Usuario = None):
    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]

    if usr_atual.role == Role.DEV:
        roles_edit = [r for r in Role]
    elif usr_atual.role == Role.CONS:
        roles_edit = [Role.ADM, Role.GEST, Role.USR, Role.CAND]
    elif usr_atual.role == Role.ADM:
        roles_edit = [Role.GEST, Role.USR, Role.CAND]

    if usr:
        desabilitar = usr.role not in roles_edit
    else:
        desabilitar = False

    data_role = [r.value for r in roles_edit]

    data_unidades = buscar_data_unidades(usr.empresa if usr else usr_atual.empresa)

    return html.Div(
        className="editar-usr",
        children=[
            html.H1("Informações Pessoais", className="secao-pagina"),
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
                        disabled=desabilitar,
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
                        disabled=desabilitar,
                    ),
                    dmc.TextInput(
                        id="email-edit-usr",
                        label="E-mail (opcional)",
                        type="email",
                        placeholder="nome@dominio.com",
                        icon=DashIconify(icon="fluent:mail-20-regular", width=20),
                        name="email",
                        value=usr.email if usr else None,
                        disabled=desabilitar,
                    ),
                    dmc.DatePicker(
                        id="data-edit-usr",
                        label="Data de Nascimento",
                        description="Será a senha do usuário",
                        locale="pt-br",
                        inputFormat="DD [de] MMMM [de] YYYY",
                        firstDayOfWeek="sunday",
                        initialLevel="year",
                        clearable=False,
                        placeholder=datetime.now().strftime(r"%d de %B de %Y"),
                        icon=DashIconify(icon="fluent:calendar-20-regular", width=20),
                        name="data",
                        value=usr.data.date() if usr else None,
                        disabled=desabilitar,
                    ),
                ],
            ),
            dmc.Divider(),
            html.H1("Informações Profissionais", className="secao-pagina"),
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
                        nothingFound="Não encontrei nada",
                        value=str(usr.empresa) if usr else str(usr_atual.empresa),
                        disabled=desabilitar or usr_atual.role == Role.ADM,
                    ),
                    dmc.Select(
                        id="cargo-edit-usr",
                        label="Cargo",
                        description="Selecione a opção que melhor se encaixa",
                        data=CARGOS_PADROES,
                        creatable=True,
                        clearable=False,
                        searchable=True,
                        nothingFound="Não encontrei nada",
                        icon=DashIconify(icon="fluent:briefcase-20-regular", width=20),
                        name="cargo",
                        value=usr.cargo if usr else None,
                        disabled=desabilitar,
                    ),
                    dmc.MultiSelect(
                        id="unidades-edit-usr",
                        label="Unidade(s)",
                        data=data_unidades,
                        value=usr.unidades if usr else None,
                        disabled=desabilitar,
                    ),
                    dmc.Select(
                        id="role-edit-usr",
                        label="Perfil",
                        icon=DashIconify(
                            icon="fluent:person-passkey-20-regular", width=20
                        ),
                        data=data_role,
                        value=usr.role.value if usr else Role.USR.value,
                        disabled=desabilitar,
                    ),
                ],
            ),
            dmc.Divider(),
            dmc.Group(
                children=[
                    dmc.Button(
                        id="btn-reset-usr-password",
                        children="Redefinir senha",
                        disabled=desabilitar,
                        leftIcon=DashIconify(
                            icon="fluent:arrow-reset-20-regular", width=20
                        ),
                    )
                    if usr
                    else None,
                    dmc.Button(
                        id="btn-salvar-usr" if usr else "btn-criar-usr",
                        children="Salvar" if usr else "Criar",
                        disabled=desabilitar,
                        leftIcon=DashIconify(icon="fluent:save-20-regular", width=20),
                        ml="auto",
                    ),
                    dmc.Button(
                        id="btn-delete-usr",
                        children="Excluir",
                        color="red",
                        disabled=desabilitar,
                        leftIcon=DashIconify(icon="fluent:delete-20-regular", width=20),
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
        ],
    )


def buscar_data_unidades(id_empresa: ObjectId) -> list[dict[str, str]]:
    empresa = Empresa.buscar("_id", id_empresa)
    return [
        {"value": unidade.cod, "label": f"({unidade.cod}) - {unidade.nome}"}
        for unidade in empresa.unidades
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

    return buscar_data_unidades(id_empresa)


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
    State("url", "href"),
    prevent_initial_call=True,
)
def salvar_usr(
    n,
    nome: str,
    cpf: str,
    _data: str,
    email: str,
    _empresa: str,
    cargo: str,
    role: str,
    unidades: list[int] | None,
    href: str,
):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_usr = href.split("/")[-1]
    data = datetime.strptime(_data, "%Y-%m-%d")
    empresa = ObjectId(_empresa)

    try:
        usr = Usuario.buscar("_id", id_usr)

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

        comps = (
            ("nome", usr.nome, nome),
            ("cpf", usr.cpf, cpf),
            ("data", usr.data, data),
            ("email", usr.email, email or None),
            ("empresa", usr.empresa, empresa),
            ("cargo", usr.cargo, cargo or None),
            ("role", usr.role, role),
            ("unidades", usr.unidades, unidades or None),
        )

        atualizacoes = {k: v_novo for k, v, v_novo in comps if v != v_novo}

        usr.atualizar(atualizacoes)

    except (ValidationError, AssertionError) as e:
        match e:
            case ValidationError():
                erro = e.errors()[0]["ctx"]["error"]
            case _:
                erro = e
        return dmc.Notification(
            id="notificacao-salvar-usr",
            title="Atenção",
            message=str(erro),
            action="show",
            color="red",
        ), no_update

    else:
        return dmc.Notification(
            id="notificacao-salvar-usr",
            title="Pronto!",
            message=[
                dmc.Text(span=True, children="O usuário "),
                dmc.Text(span=True, children=nome, weight=700),
                dmc.Text(span=True, children=" foi modificado com sucesso."),
            ],
            color="green",
            action="show",
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
def criar_novo_usr(
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

    if not usr_atual.is_authenticated:
        raise PreventUpdate

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
                    f"Não você não tem permissão para atribuir este perfil: {role.capitalize()}."
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
        return dmc.Notification(
            id="notificacao-erro-edit-usr",
            title="Atenção",
            message=str(erro),
            action="show",
            color="red",
        ), no_update

    else:
        return dmc.Notification(
            id="notificacao-novo-usr-suc",
            title="Pronto!",
            message=f"O usuário {usr.nome} foi criado com sucesso",
            color="green",
            action="show",
        ), "/app/admin/usuarios"


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("confirm-delete-usr", "displayed"),
    Input("btn-delete-usr", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "href", allow_duplicate=True),
    Input("confirm-delete-usr", "submit_n_clicks"),
    State("url", "search"),
    prevent_initial_call=True,
)
def excluir_usr(n: int, search: str):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    params = parse_qs(search[1:])
    id_usr = params["id"][0]

    r = db("Boopt", "Usuários").delete_one(
        {"_id": ObjectId(id_usr), "empresa": usr_atual.empresa}
    )

    if not r.acknowledged:
        return dmc.Notification(
            id="notificacao-excluir-usr",
            title="Atenção",
            message="Houve um erro ao excluir o usuário. Tente novamente mais tarde.",
            color="red",
            action="show",
        ), no_update

    return dmc.Notification(
        id="notificacao-excluir-usr",
        title="Pronto!",
        message="O usuário foi excluído com sucesso.",
        color="green",
        action="show",
    ), "/app/admin/usuarios"


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("confirm-reset-usr-password", "displayed"),
    Input("btn-reset-usr-password", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("confirm-reset-usr-password", "submit_n_clicks"),
    State("url", "search"),
    prevent_initial_call=True,
)
def redefinir_senha(n: int, search: str):
    usr_atual = Usuario.atual()

    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if not usr_atual.is_authenticated:
        raise PreventUpdate

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    else:
        params = parse_qs(search[1:])
        id_usr = params["id"][0]

        usr = Usuario.buscar("_id", id_usr)

        nova_senha = usr.data.strftime("%d%m%Y")

        r = db("Boopt", "Usuários").update_one(
            {"_id": ObjectId(id_usr), "empresa": usr_atual.empresa},
            update={"$set": {"senha_hash": generate_password_hash(nova_senha)}},
        )

        if not r.acknowledged:
            NOTIFICACAO = dmc.Notification(
                id="notificacao-reset-usr-password",
                title="Atenção",
                message="Houve um erro ao redefinir a senha. Tente novamente mais tarde.",
                color="red",
                action="show",
            )

        else:
            NOTIFICACAO = dmc.Notification(
                id="notificacao-excluir-usr",
                title="Pronto!",
                message=f"A senha do usuário {usr.nome} foi redefinida com sucesso",
                color="green",
                action="show",
            )

    return NOTIFICACAO
