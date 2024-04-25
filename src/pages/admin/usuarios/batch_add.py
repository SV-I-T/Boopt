import base64
import io

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
from flask_login import current_user
from pydantic import ValidationError
from utils.modelo_usuario import (
    CARGOS_PADROES,
    NovosUsuariosBatelada,
    Role,
    Usuario,
    checar_perfil,
)

register_page(
    __name__, path="/app/admin/usuarios/cadastro-massa", title="Cadastro em Massa"
)


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout():
    usr_atual: Usuario = current_user

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

    data_role = [{"value": r.value, "label": r.name.capitalize()} for r in roles_edit]

    return [
        html.H1("Cadastro em massa", className="titulo-pagina"),
        html.Div(
            className="grid grid-2-col",
            children=[
                html.Div(
                    [
                        dmc.Select(
                            id="empresa-usr-massa",
                            label="Empresa dos usuários",
                            icon=DashIconify(
                                icon="fluent:building-20-filled", width=20
                            ),
                            name="empresa",
                            data=data_empresas,
                            value=str(usr_atual.empresa),
                            placeholder="Selecione uma empresa",
                            searchable=True,
                            nothingFound="Não encontrei nada",
                            w=300,
                            display="none" if usr_atual.perfil == Role.ADM else "block",
                        ),
                        dmc.Select(
                            id="perfil-usr-massa",
                            label="Perfil dos usuários",
                            icon=DashIconify(
                                icon="fluent:person-passkey-20-filled", width=20
                            ),
                            name="perfil",
                            data=data_role,
                            value=Role.USR,
                            placeholder="Selecione um perfil",
                            w=300,
                        ),
                        html.H1("Importe seu arquivo excel", className="secao-pagina"),
                        dcc.Upload(
                            id="upload-cadastro-massa",
                            className="container-upload",
                            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            style_active={},
                            style_reject={},
                            className_active="upload-ativo",
                            className_reject="upload-negado",
                            max_size=5e6,
                            children=[
                                "Arraste aqui ou ",
                                html.A("selecione um arquivo"),
                                # DashIconify(
                                #     icon="fluent:document-add-48-regular",
                                #     width=48,
                                #     color="#1717FF",
                                # ),
                                dmc.Text(
                                    "Tamanho máximo: 5MB",
                                    size=14,
                                    opacity=0.5,
                                ),
                                html.Div(
                                    id="div-usr-massa-arquivo",
                                    children=[
                                        dmc.Divider(w="100%"),
                                        dmc.Group(
                                            children=[
                                                DashIconify(
                                                    icon="vscode-icons:file-type-excel",
                                                    width=24,
                                                ),
                                                dmc.Text(id="usr-massa-arquivo"),
                                            ],
                                        ),
                                    ],
                                    style={"display": "none"},
                                ),
                            ],
                        ),
                        dmc.Button("Enviar", id="btn-criar-usrs-batelada"),
                        html.Div(id="feedback-usr-massa"),
                    ]
                ),
                html.Div(
                    [
                        html.P(
                            "A importação é indicada para quando há a necessidade de adicionar uma grande quantidade de usuários ao mesmo tempo. Por padrão, a senha do usuário será definida como sua data de aniversário, no formato DDMMAAAA"
                        ),
                        html.H1(
                            "Precisa de ajuda para importar seu arquivo?",
                            className="secao-pagina",
                        ),
                        html.P(
                            "Faça o download do arquivo de modelo abaixo, e preencha-o de acordo."
                        ),
                        dmc.Button(
                            id="usr-massa-download-template",
                            children="Baixar modelo",
                            leftIcon=DashIconify(
                                icon="fluent:arrow-download-16-filled", width=16
                            ),
                        ),
                        html.H1("Como preencher o modelo?", className="secao-pagina"),
                        dcc.Markdown("""
Para que todos os usuários sejam validados e cadastrados, é necessário que o arquivo seja preenchido corretamente. Siga as dicas abaixo para não ter nenhum problema:
* Não modifique o cabeçalho da planilha;
* Não adicione novos campos e não remova campos existentes;
"""),
                    ]
                ),
            ],
        ),
    ]


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("usr-massa-download-template", "n_clicks"),
    prevent_initial_call=True,
)
def baixar_template_cadastro_massa(n):
    if not n:
        raise PreventUpdate

    return dcc.send_file("./assets/template_cadastro.xlsx")
    buffer = io.BytesIO()
    wb = NovosUsuariosBatelada.gerar_modelo(cargos_padres=CARGOS_PADROES)
    wb.save(buffer)
    wb.close()
    return dcc.send_bytes(
        src=buffer.getvalue(),
        filename="template_cadastro.xlsx",
        type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


clientside_callback(
    ClientsideFunction("clientside", "upload_arquivo_usr_batelada"),
    Output("usr-massa-arquivo", "children"),
    Input("upload-cadastro-massa", "filename"),
    prevent_initial_call=True,
)


@callback(
    Output("feedback-usr-massa", "children"),
    Output("notificacoes", "children", allow_duplicate=True),
    Output("url", "pathname", allow_duplicate=True),
    Input("btn-criar-usrs-batelada", "n_clicks"),
    State("upload-cadastro-massa", "contents"),
    State("upload-cadastro-massa", "filename"),
    State("empresa-usr-massa", "value"),
    State("perfil-usr-massa", "value"),
    prevent_initial_call=True,
)
def carregar_arquivo_xlsx(n: int, contents: str, nome: str, empresa: str, role: str):
    if not n:
        raise PreventUpdate
    if not empresa:
        ALERTA = dmc.Alert(
            title="Atenção",
            children="Selecione uma empresa para cadastrar os usuários.",
            color="BooptLaranja",
        )
        NOTIFICACAO = no_update
        URL = no_update
    elif not role:
        ALERTA = dmc.Alert(
            title="Atenção",
            children="Selecione um perfil para cadastrar os usuários.",
            color="BooptLaranja",
        )
        NOTIFICACAO = no_update
        URL = no_update
    elif not contents:
        ALERTA = dmc.Alert(
            title="Atenção",
            children="Selecione um arquivo com os dados dos usuários.",
            color="BooptLaranja",
        )
        NOTIFICACAO = no_update
        URL = no_update
    elif not nome.endswith(".xlsx"):
        ALERTA = dmc.Alert(
            title="Atenção",
            children='O arquivo precisa ter a extensão ".xlsx".',
            color="BooptLaranja",
        )
        NOTIFICACAO = no_update
        URL = no_update
    else:
        try:
            _, content_string = contents.split(",")
            decoded = base64.b64decode(content_string)
            novos_usuarios = NovosUsuariosBatelada.carregar_planilha(
                io.BytesIO(decoded), empresa=ObjectId(empresa), role=Role(role)
            )
            novos_usuarios.registrar_usuarios()
        except ValidationError as e:
            ALERTA = dmc.Alert(
                className="alert-erros",
                title=f"{e.error_count()} erros encontrados",
                children=[
                    dcc.Markdown(
                        f'**Linha {erro["loc"][1]+1}**: {erro["ctx"]["error"]}'
                    )
                    for erro in e.errors()
                ],
                color="BooptLaranja",
            )
            NOTIFICACAO = no_update
            URL = no_update
        except Exception as e:
            ALERTA = dmc.Alert(
                title="Atenção",
                children=str(e),
                color="BooptLaranja",
            )
            NOTIFICACAO = no_update
            URL = no_update
        else:
            ALERTA = None
            NOTIFICACAO = dmc.Notification(
                id="notificacao-usr-massa-suc",
                action="show",
                title="Pronto!",
                message=f"{len(novos_usuarios.usuarios)} usuários foram criados com sucesso.",
                color="green",
            )
            URL = "/app/admin/usuarios"

    return ALERTA, NOTIFICACAO, URL
