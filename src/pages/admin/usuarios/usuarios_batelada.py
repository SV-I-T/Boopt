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
from pydantic import ValidationError
from utils.banco_dados import db
from utils.modelo_usuario import (
    CARGOS_PADROES,
    NovosUsuariosBatelada,
    Perfil,
    checar_perfil,
)

register_page(
    __name__, path="/app/admin/usuarios/cadastro-massa", title="Cadastro em Massa"
)


@checar_perfil(permitir=[Perfil.dev, Perfil.admin, Perfil.gestor])
def layout():
    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in db("Boopt", "Empresas").find(
            projection={"_id": 1, "nome": 1}, sort={"nome": 1}
        )
    ]
    return [
        dmc.Title("Cadastro em massa", className="titulo-pagina"),
        dmc.Select(
            id="empresa-usr-massa",
            label="Empresa de cadastro",
            icon=DashIconify(icon="fluent:building-24-filled", width=24),
            name="empresa",
            data=data_empresas,
            placeholder="Selecione uma empresa",
            required=True,
            searchable=True,
            nothingFound="Não encontrei nada",
            w=300,
        ),
        dmc.Button(
            id="usr-massa-download-template",
            children="Baixar modelo",
            variant="subtle",
            compact=True,
            leftIcon=DashIconify(icon="fluent:arrow-download-16-filled", width=16),
        ),
        dcc.Upload(
            id="upload-cadastro-massa",
            className="container-upload",
            accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            children=[
                html.Div(
                    [
                        dmc.Text(
                            "Clique aqui para selecionar ou arraste o arquivo (.xlsx)"
                        ),
                        dmc.Text(
                            id="usr-massa-arquivo", children="Nenhum arquivo escolhido"
                        ),
                    ]
                ),
            ],
        ),
        dmc.Button("Enviar", id="btn-criar-usrs-batelada"),
        html.Div(id="feedback-usr-massa"),
    ]


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("usr-massa-download-template", "n_clicks"),
    prevent_initial_call=True,
)
def baixar_template_cadastro_massa(n):
    if not n:
        raise PreventUpdate

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
    ClientsideFunction("clientside", "bind_valor"),
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
    prevent_initial_call=True,
)
def carregar_arquivo_xlsx(n: int, contents: str, nome: str, empresa: str):
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
                io.BytesIO(decoded)
            )
            novos_usuarios.registrar_usuarios(empresa=ObjectId(empresa))
        except ValidationError as e:
            ALERTA = dmc.Alert(
                title="Atenção",
                children=str(e.errors()[0]["ctx"]["error"]),
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
