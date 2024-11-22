import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, dcc, html, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils import Role, Usuario, checar_perfil, db, nova_notificacao

register_page(__name__, path="/app/admin/consultores", title="Consultores")


@checar_perfil(permitir=(Role.DEV,))
def layout():
    data_consultores = list(db("ViewUsuáriosConsultores").find())

    data_row_empresas = list(
        db("Empresas").find(
            {}, {"_id": 0, "id": {"$toString": "$_id"}, "nome": 1, "segmento": 1}
        )
    )
    return [
        html.H1([dcc.Link("", href="/app/admin", title="Voltar"), "Consultores"]),
        dmc.Stack(
            children=[
                dmc.Select(
                    id="select-consultor-cliente",
                    label="Consultor",
                    data=data_consultores,
                    placeholder="Selecione",
                ),
                dmc.Text(id="text-consultor-qtde-clientes"),
                dag.AgGrid(
                    id="table-consultores-clientes",
                    className="ag-theme-quartz compact",
                    columnDefs=[
                        {"field": "id", "hide": True},
                        {
                            "field": "nome",
                            "headerName": "Empresa",
                            "checkboxSelection": True,
                            "headerCheckboxSelection": True,
                            "headerCheckboxSelectionFilteredOnly": True,
                        },
                        {"field": "segmento", "headerName": "Segmento"},
                    ],
                    getRowId="params.data.id",
                    rowData=data_row_empresas,
                    selectedRows=[],
                    dashGridOptions={
                        "rowSelection": "multiple",
                        "suppressRowClickSelection": True,
                        "overlayLoadingTemplate": {
                            "function": "'<span>Selecione uma empresa primeiro</span>'"
                        },
                        "overlayNoRowsTemplate": {
                            "function": "'<span>Não há registros</span>'"
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
                ),
                dmc.Group(
                    children=[
                        dmc.Button(
                            id="btn-salvar-clientes-consultor",
                            children="Salvar",
                            leftIcon=DashIconify(
                                icon="fluent:checkmark-20-regular", width=20
                            ),
                        ),
                    ]
                ),
            ]
        ),
    ]


@callback(
    Output("table-consultores-clientes", "selectedRows"),
    Output("text-consultor-qtde-clientes", "children"),
    Input("select-consultor-cliente", "value"),
    prevent_initial_call=True,
)
def atualizar_clientes_selecionados(_id_consultor: str):
    usr_atual = Usuario.atual()
    if usr_atual.role != Role.DEV:
        raise PreventUpdate
    id_consultor = ObjectId(_id_consultor)
    usr = db("Usuários").find_one({"_id": id_consultor}, {"_id": 0, "clientes": 1})
    if "clientes" not in usr:
        return [], "0 clientes"
    return [
        {"id": str(id)} for id in usr["clientes"]
    ], f"{len(usr['clientes'])} clientes"


@callback(
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-salvar-clientes-consultor", "n_clicks"),
    State("select-consultor-cliente", "value"),
    State("table-consultores-clientes", "selectedRows"),
    prevent_initial_call=True,
)
def salvar_clientes_consultor(
    n: int, _id_consultor: str, clientes_selecionados: list[dict[str, str]]
):
    if not n:
        raise PreventUpdate

    if not _id_consultor:
        return nova_notificacao(
            id="feedback-clientes-consultor",
            message="Selecione um consultor",
            type="error",
        )
    usr_atual = Usuario.atual()

    if usr_atual.role != Role.DEV:
        raise PreventUpdate

    id_consultor = ObjectId(_id_consultor)
    ids_clientes = [ObjectId(cliente["id"]) for cliente in clientes_selecionados]

    if ids_clientes:
        update = {"$set": {"clientes": ids_clientes}}
    else:
        update = {"$unset": {"clientes": 1}}

    r = db("Usuários").update_one({"_id": id_consultor}, update=update)

    if not r.acknowledged:
        return nova_notificacao(
            id="feedback-clientes-consultor",
            message="Ocorreu algo de errado ao tentar editar os clientes. Tente novamente mais tarde.",
            type="error",
        )

    return nova_notificacao(
        id="feedback-clientes-consultor",
        message="Os clientes foram editados com sucesso.",
        type="success",
    )
