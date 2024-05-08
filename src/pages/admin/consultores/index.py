import dash_ag_grid as dag
import dash_mantine_components as dmc
from bson import ObjectId
from dash import Input, Output, State, callback, html, register_page
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from utils.banco_dados import db
from utils.login import checar_perfil
from utils.role import Role
from utils.usuario import Usuario

register_page(__name__, path="/app/admin/consultores", title="Gestão de consultores")


@checar_perfil(permitir=(Role.DEV,))
def layout():
    usr_atual = Usuario.atual()

    data_consultores = [
        {"value": consultor["_id"], "label": consultor["nome"]}
        for consultor in db("Boopt", "Usuários").find(
            {"role": Role.CONS},
            {
                "_id": {"$toString": "$_id"},
                "nome": 1,
            },
        )
    ]

    data_row_empresas = [
        {
            "id": str(empresa["_id"]),
            "nome": empresa["nome"],
            "segmento": empresa["segmento"],
        }
        for empresa in usr_atual.buscar_empresas(
            project_fields=["_id", "nome", "segmento"]
        )
    ]
    return [
        html.H1("Gestão de consultores", className="titulo-pagina"),
        dmc.Select(
            id="select-consultor-cliente",
            label="Consultor",
            data=data_consultores,
        ),
        dmc.Text(id="text-consultor-qtde-clientes", children="Selecione um consultor"),
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
                    ml="auto",
                    leftIcon=DashIconify(icon="fluent:save-20-regular", width=20),
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
    usr = db("Boopt", "Usuários").find_one(
        {"_id": id_consultor}, {"_id": 0, "clientes": 1}
    )
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
        return dmc.Notification(
            id="notificacao-edit-clientes-consultor",
            title="Atenção",
            message="Selecione um consultor",
            action="show",
            color="red",
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

    r = db("Boopt", "Usuários").update_one({"_id": id_consultor}, update=update)

    if not r.acknowledged:
        return dmc.Notification(
            title="Atenção",
            message="Ocorreu algo de errado ao tentar editar os clientes. Tente novamente mais tarde.",
            action="show",
            color="red",
        )

    return dmc.Notification(
        id="notificacao-edit-clientes-consultor",
        title="Pronto!",
        message="Os clientes foram editados com sucesso.",
        action="show",
        color="green",
    )
