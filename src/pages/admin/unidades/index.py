import base64
import io

import dash_mantine_components as dmc
import polars as pl
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
from pymongo import UpdateMany

from utils import Empresa, Role, Usuario, checar_perfil, db, nova_notificacao

register_page(__name__, path="/app/admin/unidades", title="Unidades")


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout():
    usr_atual = Usuario.atual()

    data_empresas = usr_atual.consultar_empresas()
    data_unidades = consultar_unidades(usr_atual.empresa)

    # Puxa todos os usuários da empresa
    data_usuarios = list(
        db("Usuários").find(
            {"empresa": usr_atual.empresa},
            {"value": {"$toString": "$_id"}, "label": "$nome", "_id": 0},
        )
    )

    return [
        html.H1("Unidades"),
        dmc.Stack(
            [
                dmc.Select(
                    id="unidades-select-empresa",
                    label="Empresa",
                    data=data_empresas,
                    value=str(usr_atual.empresa),
                    display=usr_atual.role != Role.ADM and "block" or "none",
                    icon=DashIconify(icon="fluent:building-20-regular", width=20),
                ),
                dmc.Modal(
                    id="unidades-modal",
                    title="Importar unidades",
                    children=modal_importar_unidades(),
                    zIndex=100000,
                ),
                dmc.Group(
                    children=[
                        dmc.Button(
                            id="unidades-download-btn",
                            children="Baixar unidades (.xlsx)",
                            leftIcon=DashIconify(
                                icon="fluent:arrow-download-20-filled", width=20
                            ),
                        ),
                        dmc.Button(
                            "Importar unidades",
                            leftIcon=DashIconify(
                                icon="fluent:open-20-regular", width=20
                            ),
                            variant="light",
                            id="unidades-modal-btn",
                        ),
                    ]
                ),
                dmc.Divider(),
                html.H2("Editar usuários das unidades"),
                dmc.Select(
                    id="unidades-select-unidade",
                    placeholder="Selecione uma unidade",
                    data=data_unidades,
                ),
                dmc.TransferList(
                    id="unidades-usuarios",
                    value=[data_usuarios, []],
                    titles=["Todos usuários", "Unidade"],
                    searchPlaceholder="Procure um usuário",
                    display="none",
                    h=300,
                ),
                dmc.Group(
                    dmc.Button(
                        "Salvar",
                        leftIcon=DashIconify(
                            icon="fluent:checkmark-20-regular", width=20
                        ),
                        id="unidades-usuarios-btn",
                    )
                ),
            ]
        ),
    ]


def modal_importar_unidades():
    return dmc.Stack(
        [
            dcc.Markdown("""
Você pode adicionar novas unidades ou editar unidades já existentes por meio da importação de uma planilha excel (.xlsx). Para facilitar o processo, recomendamos que baixe a planilha pelo botão acima, edite a mesma e depois faça a importação. É importante que não haja nenhuma mudança nas colunas, caso contrário você receberá um erro.

Cada unidade deve sempre conter um código único e numérico de identificação e um nome descritivo.

Para a edição de unidades já existentes, você pode alterar o nome a vontade, porém recomendamos que o código sempre permaneca o mesmo, pois é a ele que vendedores e gerentes/supervisores estarão associados.
"""),
            dcc.Upload(
                id="unidades-upload",
                className="container-upload",
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                style_active={},
                style_reject={},
                className_active="upload-ativo",
                className_reject="upload-negado",
                max_size=2e6,
                children=[
                    "Arraste aqui ou ",
                    html.A("selecione o arquivo"),
                    dmc.Text(
                        "Tamanho máximo: 2MB",
                        size=14,
                        opacity=0.5,
                    ),
                    html.Div(
                        id="div-empresa-unidades-arquivo",
                        children=[
                            dmc.Divider(w="100%"),
                            dmc.Group(
                                children=[
                                    DashIconify(
                                        icon="vscode-icons:file-type-excel",
                                        width=24,
                                    ),
                                    dmc.Text(id="unidades-arquivo"),
                                ],
                            ),
                        ],
                        style={"display": "none"},
                    ),
                ],
            ),
            dmc.Button(
                "Importar",
                id="unidades-import-btn",
                leftIcon=DashIconify(icon="fluent:arrow-upload-20-regular", width=20),
            ),
            html.Div(id="unidades-import-feedback"),
        ]
    )


def consultar_unidades(id_empresa: ObjectId) -> list[dict[str, str]]:
    empresa = Empresa.consultar("_id", id_empresa)
    return [
        {"value": unidade.cod, "label": unidade.nome} for unidade in empresa.unidades
    ]


def consultar_usuarios(
    id_empresa: ObjectId, unidade: int = None
) -> tuple[list[str], list[str]]:
    usuarios = db("Usuários").find({"empresa": id_empresa}, {"nome": 1, "unidades": 1})

    lista_usuarios = [[], []]

    for usuario in usuarios:
        if unidade and "unidades" in usuario and unidade in usuario["unidades"]:
            lista_usuarios[1].append(
                {"value": str(usuario["_id"]), "label": usuario["nome"]}
            )
        else:
            lista_usuarios[0].append(
                {"value": str(usuario["_id"]), "label": usuario["nome"]}
            )

    return lista_usuarios


clientside_callback(
    ClientsideFunction("interacoes", "ativar"),
    Output("unidades-modal", "opened"),
    Input("unidades-modal-btn", "n_clicks"),
)


@callback(
    Output("unidades-select-unidade", "data"),
    Output("unidades-select-unidade", "value"),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("unidades-select-empresa", "value"),
    prevent_initial_call=True,
)
def atualizar_lista_unidades(_id_empresa: str):
    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_empresa = ObjectId(_id_empresa)
    if usr_atual.role == Role.ADM and usr_atual.empresa != id_empresa:
        return (
            no_update,
            no_update,
            nova_notificacao(
                id="feedback-unidades",
                type="error",
                message="Você não é administrador dessa empresa.",
            ),
        )

    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        return (
            no_update,
            no_update,
            nova_notificacao(
                id="feedback-unidades",
                type="error",
                message="Você não é consultor dessa empresa.",
            ),
        )

    data_unidades = consultar_unidades(id_empresa)
    return data_unidades, None, no_update


@callback(
    Output("unidades-usuarios", "value"),
    Output("unidades-usuarios", "display"),
    Input("unidades-select-unidade", "value"),
    State("unidades-select-empresa", "value"),
    State("unidades-usuarios", "value"),
    prevent_initial_call=True,
)
def atualizar_colaboradores_unidade(
    unidade: int,
    _id_empresa: str,
    data_usuarios: tuple[list[dict[str, str]], list[dict[str, str]]],
):
    if not unidade:
        return no_update, "none"

    usuarios_na_unidade = [
        str(u["_id"])
        for u in db("Usuários").find(
            {"empresa": ObjectId(_id_empresa), "unidades": unidade}, {"_id": 1}
        )
    ]

    usuarios = data_usuarios[0] + data_usuarios[1]

    novo_data_usuarios: tuple[list[dict[str, str]], list[dict[str, str]]] = [[], []]
    for usuario in usuarios:
        if usuario["value"] in usuarios_na_unidade:
            novo_data_usuarios[1].append(usuario)
        else:
            novo_data_usuarios[0].append(usuario)

    return novo_data_usuarios, "grid"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("unidades-usuarios-btn", "n_clicks"),
    State("unidades-select-unidade", "value"),
    State("unidades-usuarios", "value"),
    State("unidades-select-empresa", "value"),
    prevent_initial_call=True,
)
def editar_usuarios_unidade(
    n: int,
    unidade: int,
    id_usuarios: tuple[list[dict[str, str]], list[dict[str, str]]],
    _id_empresa: str,
):
    if not n:
        raise PreventUpdate

    id_empresa = ObjectId(_id_empresa)
    id_usuarios_na_unidade = [
        ObjectId(id_usuario["value"]) for id_usuario in id_usuarios[1]
    ]

    r = db("Usuários").bulk_write(
        [
            # Retirar a unidade de todos
            UpdateMany(
                filter={"empresa": id_empresa},
                update={"$pull": {"unidades": unidade}},
            ),
            # Adicionar a unidade nos usuarios
            UpdateMany(
                filter={
                    "empresa": id_empresa,
                    "_id": {"$in": id_usuarios_na_unidade},
                },
                update={"$push": {"unidades": unidade}},
            ),
        ]
    )

    if not r.acknowledged:
        return nova_notificacao(
            id="feedback-unidades",
            type="error",
            message="Houve algum erro ao editar os usuários dessa unidade. Tente novamente mais tarde.",
        )

    return nova_notificacao(
        id="feedback-unidades",
        type="success",
        message="Os usuários da unidade foram salvos.",
    )


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("unidades-download-btn", "n_clicks"),
    State("unidades-select-unidade", "data"),
    prevent_initial_call=True,
)
def baixar_unidades(n: int, data: dict):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    df_unidades = pl.DataFrame(data, schema={"value": int, "label": str}).rename(
        {"value": "Código", "label": "Unidade"}
    )
    buf = io.BytesIO()
    df_unidades.write_excel(buf)
    buf.seek(0)

    return dcc.send_bytes(buf.getvalue(), filename="Boopt - Unidades.xlsx")


clientside_callback(
    ClientsideFunction("clientside", "upload_arquivo_empresa_unidades"),
    Output("unidades-arquivo", "children"),
    Input("unidades-upload", "filename"),
    prevent_initial_call=True,
)


@callback(
    Output("unidades-import-feedback", "children"),
    Output("notificacoes", "children", allow_duplicate=True),
    Output("unidades-modal", "opened", allow_duplicate=True),
    Input("unidades-import-btn", "n_clicks"),
    State("unidades-upload", "contents"),
    State("unidades-upload", "filename"),
    State("unidades-select-empresa", "value"),
    prevent_initial_call=True,
)
def carregar_arquivo_unidades(n: int, contents: str, nome: str, _id_empresa: str):
    if not n:
        raise PreventUpdate

    id_empresa = ObjectId(_id_empresa)
    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    if usr_atual.role == Role.ADM and usr_atual.empresa != id_empresa:
        return (
            no_update,
            nova_notificacao(
                id="feedback-unidades",
                type="error",
                message="Você não é administrador dessa empresa",
            ),
            no_update,
        )

    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        return (
            no_update,
            nova_notificacao(
                id="feedback-unidades",
                type="error",
                message="Você não é consultor dessa empresa",
            ),
            no_update,
        )

    if not contents:
        return (
            dmc.Alert(
                title="Ops!",
                children="Selecione um arquivo com os dados das unidades.",
                color="BooptLaranja",
            ),
            no_update,
            no_update,
        )

    elif not nome.endswith(".xlsx"):
        return (
            dmc.Alert(
                title="Ops!",
                children='O arquivo precisa ter a extensão ".xlsx".',
                color="BooptLaranja",
            ),
            no_update,
            no_update,
        )
    else:
        try:
            _, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)

            df_unidades = pl.read_excel(io.BytesIO(decoded))
            assert (
                df_unidades.columns == ["Código", "Unidade"]
            ), "Certifique-se que a planilha tenha somente as colunas 'Código' e 'Unidade'"

            assert (
                df_unidades.get_column("Código").dtype in pl.INTEGER_DTYPES
            ), "Os códigos das unidades precisam ser números inteiros"

            unidades_duplicadas = (
                df_unidades.filter(pl.col("Código").is_duplicated())
                .get_column("Código")
                .unique()
                .cast(pl.Utf8)
                .to_list()
            )
            assert (
                len(unidades_duplicadas) == 0
            ), f"Foram encontradas múltiplas unidades com o mesmo código: {', '.join(unidades_duplicadas)}"

            unidades = df_unidades.rename(
                {"Código": "cod", "Unidade": "nome"}
            ).to_dicts()
            r = db("Empresas").update_one(
                {"_id": id_empresa}, update={"$set": {"unidades": unidades}}
            )
            assert r.acknowledged, "Ocorreu algum erro ao atualizar as unidades. Tente novamente mais tarde."

        except Exception as e:
            return (
                dmc.Alert(
                    title="Ops!",
                    children=str(e),
                    color="BooptLaranja",
                ),
                no_update,
                no_update,
            )

        else:
            return (
                None,
                nova_notificacao(
                    id="feedback-unidades",
                    type="success",
                    message="As unidades foram atualizadas com sucesso.",
                ),
                False,
            )
