import base64
import io

import dash_ag_grid as dag
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
from utils.banco_dados import db
from utils.empresa import Empresa
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, path="/app/admin/unidades", title="Unidades")


@checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM))
def layout():
    usr_atual = Usuario.atual()

    data_empresas = [
        {"value": str(empresa["_id"]), "label": empresa["nome"]}
        for empresa in usr_atual.buscar_empresas()
    ]

    data_unidades = buscar_unidades(usr_atual.empresa)

    return [
        html.H1("Unidades", className="titulo-pagina"),
        dmc.Stack(
            [
                dmc.Select(
                    id="select-empresa-unidades",
                    label="Empresa",
                    data=data_empresas,
                    value=str(usr_atual.empresa),
                    display=usr_atual.role != Role.ADM and "block" or "none",
                ),
                dag.AgGrid(
                    id="table-empresa-unidades",
                    className="ag-theme-quartz compact",
                    columnDefs=[
                        {"field": "cod", "headerName": "Código"},
                        {"field": "nome", "headerName": "Unidade"},
                    ],
                    getRowId="params.data.cod",
                    rowData=data_unidades,
                    selectedRows=[],
                    dashGridOptions={
                        "rowSelection": "multiple",
                        "suppressRowClickSelection": True,
                        "overlayLoadingTemplate": {
                            "function": "'<span>Carregando...</span>'"
                        },
                        "overlayNoRowsTemplate": {
                            "function": "'<span>Não há unidades cadastradas</span>'"
                        },
                    },
                    defaultColDef={
                        "resizable": False,
                        "filter": True,
                        "floatingFilter": True,
                        "floatingFilterComponentParams": {
                            "suppressFilterButton": True,
                        },
                        "suppressMenu": True,
                        "suppressMovable": True,
                        "flex": 1,
                    },
                    columnSize="autoSize",
                    columnSizeOptions={"keys": ["cod"]},
                    style={"width": 500},
                ),
                dmc.Button(
                    id="btn-download-empresa-unidades",
                    children="Baixar unidades (.xlsx)",
                    leftIcon=DashIconify(
                        icon="fluent:arrow-download-16-filled", width=16
                    ),
                ),
                html.H1("Importar unidades", className="secao-pagina"),
                dcc.Markdown("""
Você pode adicionar novas unidades ou editar unidades já existentes por meio da importação de uma planilha excel (.xlsx). Para facilitar o processo, recomendamos que baixe a planilha pelo botão acima, edite a mesma e depois faça a importação. É importante que não haja nenhuma mudança nas colunas, caso contrário você receberá um erro.

Cada unidade deve sempre conter um código único e numérico de identificação e um nome descritivo.

Para a edição de unidades já existentes, você pode alterar o nome a vontade, porém recomendamos que o código sempre permaneca o mesmo, pois é a ele que vendedores e gerentes/supervisores estarão associados.
"""),
                dcc.Upload(
                    id="upload-empresa-unidades",
                    className="container-upload",
                    accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    style_active={},
                    style_reject={},
                    className_active="upload-ativo",
                    className_reject="upload-negado",
                    max_size=2e6,
                    children=[
                        "Arraste aqui ou ",
                        html.A("selecione um arquivo"),
                        "(.xlsx)",
                        # DashIconify(
                        #     icon="fluent:document-add-48-regular",
                        #     width=48,
                        #     color="#1717FF",
                        # ),
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
                                        dmc.Text(id="empresa-unidades-arquivo"),
                                    ],
                                ),
                            ],
                            style={"display": "none"},
                        ),
                    ],
                ),
                dmc.Button("Importar", id="btn-salvar-empresa-unidades"),
                html.Div(id="feedback-empresa-unidades"),
            ]
        ),
    ]


def buscar_unidades(id_empresa: ObjectId) -> list[dict[str, str]]:
    empresa = Empresa.buscar("_id", id_empresa)
    return [unidade.model_dump() for unidade in empresa.unidades]


@callback(
    Output("table-empresa-unidades", "rowData"),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("select-empresa-unidades", "value"),
    prevent_initial_call=True,
)
def atualizar_tabela_unidades(_id_empresa: str):
    usr_atual = Usuario.atual()
    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    id_empresa = ObjectId(_id_empresa)
    if usr_atual.role == Role.ADM and usr_atual.empresa != id_empresa:
        return no_update, dmc.Notification(
            id="notif-buscar-unidades",
            title="Erro de autorização",
            message="Você não é administrador dessa empresa.",
            action="show",
            color="red",
        )

    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        return no_update, dmc.Notification(
            id="notif-buscar-unidades",
            title="Erro de autorização",
            message="Você não é consultor dessa empresa.",
            action="show",
            color="red",
        )

    data_unidades = buscar_unidades(id_empresa)
    return data_unidades, no_update


@callback(
    Output("download", "data", allow_duplicate=True),
    Input("btn-download-empresa-unidades", "n_clicks"),
    State("table-empresa-unidades", "rowData"),
    prevent_initial_call=True,
)
def baixar_unidades(n: int, row_data: dict):
    if not n:
        raise PreventUpdate

    usr_atual = Usuario.atual()

    if usr_atual.role not in (Role.DEV, Role.CONS, Role.ADM):
        raise PreventUpdate

    df_unidades = pl.DataFrame(row_data, schema={"cod": int, "nome": str}).rename(
        {"cod": "Código", "nome": "Unidade"}
    )
    buf = io.BytesIO()
    df_unidades.write_excel(buf)
    buf.seek(0)

    return dcc.send_bytes(buf.getvalue(), filename="Boopt - Unidades.xlsx")


clientside_callback(
    ClientsideFunction("clientside", "upload_arquivo_empresa_unidades"),
    Output("empresa-unidades-arquivo", "children"),
    Input("upload-empresa-unidades", "filename"),
    prevent_initial_call=True,
)


@callback(
    Output("feedback-empresa-unidades", "children"),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-salvar-empresa-unidades", "n_clicks"),
    State("upload-empresa-unidades", "contents"),
    State("upload-empresa-unidades", "filename"),
    State("select-empresa-unidades", "value"),
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
        return no_update, dmc.Notification(
            id="notif-salvar-unidades",
            title="Erro de autorização",
            message="Você não é administrador dessa empresa",
            action="show",
            color="red",
        )

    if usr_atual.role == Role.CONS and id_empresa not in usr_atual.clientes:
        return no_update, dmc.Notification(
            id="notif-salvar-unidades",
            title="Erro de autorização",
            message="Você não é consultor dessa empresa",
            action="show",
            color="red",
        )

    if not contents:
        return dmc.Alert(
            title="Atenção",
            children="Selecione um arquivo com os dados das unidades.",
            color="BooptLaranja",
        ), no_update

    elif not nome.endswith(".xlsx"):
        return dmc.Alert(
            title="Atenção",
            children='O arquivo precisa ter a extensão ".xlsx".',
            color="BooptLaranja",
        ), no_update
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
            return dmc.Alert(
                title="Atenção",
                children=str(e),
                color="BooptLaranja",
            ), no_update

        else:
            return None, dmc.Notification(
                id="notif-salvar-unidades",
                action="show",
                title="Pronto!",
                message="As unidades foram atualizadas com sucesso.",
                color="green",
            )
