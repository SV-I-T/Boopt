# import dash_ag_grid as dag
# import dash_mantine_components as dmc
# import polars as pl
# from bson import ObjectId
# from dash import (
#     ClientsideFunction,
#     Input,
#     Output,
#     State,
#     callback,
#     clientside_callback,
#     html,
#     no_update,
#     register_page,
# )
# from dash.exceptions import PreventUpdate
# from dash_chartjs import ChartJs
# from dash_iconify import DashIconify
# from icecream import ic

# from utils.banco_dados import db
# from utils.login import checar_perfil
# from utils.role import Role
# from utils.usuario import Usuario
# from utils.vela import Vela

# register_page(
#     __name__, path="/app/admin/vela/dashboard", title="Dashboard Vela Assessment"
# )


# @checar_perfil(permitir=(Role.DEV, Role.CONS, Role.ADM, Role.GEST))
# def layout():
#     usr_atual = Usuario.atual()

#     data_empresas = usr_atual.consultar_empresas()
#     valor_empresa = usr_atual.empresa

#     data_gestores = consultar_gestores(valor_empresa)

#     painel_filtros = [
#         dmc.Select(
#             id="adm-results-vela-empresa",
#             label="Empresa",
#             data=data_empresas,
#             value=str(valor_empresa),
#             icon=DashIconify(icon="fluent:building-24-regular", width=24),
#             searchable=True,
#             nothingFound="Não encontramos nada",
#             display="block" and (usr_atual.role in (Role.DEV, Role.CONS)) or "none",
#         ),
#         dmc.MultiSelect(
#             id="adm-results-vela-gestores",
#             label=[
#                 "Gestores",
#                 dmc.Button(
#                     id="adm-results-vela-gestores-all",
#                     children="Todos",
#                     compact=True,
#                     variant="subtle",
#                     size="xs",
#                     ml="0.5rem",
#                 ),
#             ],
#             placeholder="Selecionar",
#             data=data_gestores,
#             clearable=True,
#         ),
#         dmc.MultiSelect(
#             id="adm-results-vela-unidades",
#             label=[
#                 "Unidades",
#                 dmc.Button(
#                     id="adm-results-vela-unidades-all",
#                     children="Todos",
#                     compact=True,
#                     variant="subtle",
#                     size="xs",
#                     ml="0.5rem",
#                 ),
#             ],
#             placeholder="Selecionar",
#             clearable=True,
#         ),
#         dmc.MultiSelect(
#             id="adm-results-vela-aplicacao",
#             label=[
#                 "Aplicação",
#                 dmc.Button(
#                     id="adm-results-vela-aplicacao-all",
#                     children="Todos",
#                     compact=True,
#                     variant="subtle",
#                     size="xs",
#                     ml="0.5rem",
#                 ),
#             ],
#             placeholder="Selecionar",
#             clearable=True,
#         ),
#         dmc.Button(
#             id="adm-results-vela-ok-btn",
#             children="Aplicar filtros",
#             rightIcon=DashIconify(icon="fluent:arrow-right-24-regular", width=24),
#         ),
#     ]

#     return [
#         dmc.Accordion(
#             children=dmc.AccordionItem(
#                 value="filtros",
#                 children=[
#                     dmc.AccordionControl(
#                         "Filtros",
#                         icon=DashIconify(icon="fluent:filter-24-regular", width=24),
#                     ),
#                     dmc.AccordionPanel(painel_filtros),
#                 ],
#             ),
#             variant="separated",
#             radius="xl",
#             value="filtros",
#         ),
#         html.Div(
#             className="vela-card-metricas",
#             children=[
#                 html.Div(
#                     className="nota-media",
#                     children=[
#                         html.Label("Nota média"),
#                         html.Span(id="adm-results-vela-nota-media"),
#                         html.Span("/70"),
#                     ],
#                 ),
#                 html.Div(
#                     className="qtd-respostas",
#                     children=[
#                         html.Span(id="adm-results-vela-qtd-respostas"),
#                         html.Label("respostas"),
#                     ],
#                 ),
#                 html.Div(
#                     className="qtd-aplicacoes",
#                     children=[
#                         html.Span(id="adm-results-vela-qtd-aplicacoes"),
#                         html.Label("aplicações"),
#                     ],
#                 ),
#             ],
#         ),
#         ChartJs(
#             id="adm-results-vela-etapas",
#             type="bar",
#             data={"datasets": [], "labels": []},
#             options={
#                 "scales": {"y": {"max": 10, "min": 0}},
#                 "plugins": {
#                     "datalabels": {
#                         "align": "end",
#                         "anchor": "end",
#                         "color": "#fff",
#                         "borderRadius": 4,
#                         "backgroundColor": "#1618ff",
#                     },
#                 },
#             },
#         ),
#         ChartJs(
#             id="adm-results-vela-competencias",
#             type="polarArea",
#             data={"datasets": [], "labels": []},
#             options={
#                 "scales": {
#                     "r": {
#                         "max": 10,
#                         "min": 0,
#                         "pointLabels": {"display": True, "centerPointLabels": True},
#                         "angleLines": {"display": True},
#                         "ticks": {"z": 10},
#                     },
#                 },
#                 "plugins": {
#                     "datalabels": {
#                         "align": "end",
#                         "anchor": "end",
#                         "color": "#fff",
#                         "borderRadius": 4,
#                     },
#                     "legend": {"display": False},
#                 },
#             },
#         ),
#         dag.AgGrid(
#             id="adm-results-vela-table",
#             dashGridOptions={
#                 "overlayLoadingTemplate": {
#                     "function": "'<span>Não há registros</span>'"
#                 },
#                 "overlayNoRowsTemplate": {
#                     "function": "'<span>Não há registros</span>'"
#                 },
#             },
#             defaultColDef={
#                 "suppressMenu": True,
#                 "suppressMovable": True,
#                 "cellStyle": {
#                     "function": "params.value && {'backgroundColor': params.value >= 8 ? '#d5fbd5': params.value < 5 ? '#ffc0c0' : '#fff'}"
#                 },
#             },
#             className="ag-theme-quartz compact",
#         ),
#     ]


# clientside_callback(
#     ClientsideFunction("clientside", "selecionar_todos"),
#     Output("adm-results-vela-gestores", "value"),
#     Input("adm-results-vela-gestores-all", "n_clicks"),
#     State("adm-results-vela-gestores", "data"),
#     prevent_initial_call=True,
# )

# clientside_callback(
#     ClientsideFunction("clientside", "selecionar_todos"),
#     Output("adm-results-vela-unidades", "value"),
#     Input("adm-results-vela-unidades-all", "n_clicks"),
#     State("adm-results-vela-unidades", "data"),
#     prevent_initial_call=True,
# )

# clientside_callback(
#     ClientsideFunction("clientside", "selecionar_todos"),
#     Output("adm-results-vela-aplicacao", "value"),
#     Input("adm-results-vela-aplicacao-all", "n_clicks"),
#     State("adm-results-vela-aplicacao", "data"),
#     prevent_initial_call=True,
# )


# def consultar_gestores(id_empresa: ObjectId) -> list[dict[str, str]]:
#     return list(
#         db("Usuários").find(
#             {"empresa": id_empresa, "role": "Gestor"},
#             {"_id": 0, "value": {"$toString": "$_id"}, "label": "$nome"},
#         )
#     )


# @callback(
#     Output("adm-results-vela-gestores", "data"),
#     Input("adm-results-vela-empresa", "value"),
#     prevent_initial_call=True,
# )
# def atualizar_gestores(id_empresa: str):
#     return consultar_gestores(ObjectId(id_empresa))


# def consultar_unidades(gestores: list[str]) -> list[dict[str, str | int]]:
#     return list(
#         db("Usuários").aggregate(
#             [
#                 {"$match": {"_id": {"$in": [ObjectId(gestor) for gestor in gestores]}}},
#                 {"$unwind": "$unidades"},
#                 {
#                     "$group": {
#                         "_id": "$empresa",
#                         "cod": {"$addToSet": "$unidades"},
#                     }
#                 },
#                 {"$unwind": "$cod"},
#                 {
#                     "$lookup": {
#                         "from": "Empresas",
#                         "let": {"empresa": "$_id", "cod": "$cod"},
#                         "pipeline": [
#                             {"$match": {"$expr": {"$eq": ["$_id", "$$empresa"]}}},
#                             {"$unwind": "$unidades"},
#                             {"$match": {"$expr": {"$eq": ["$unidades.cod", "$$cod"]}}},
#                             {"$project": {"_id": 0, "nome": "$unidades.nome"}},
#                         ],
#                         "as": "nome",
#                     },
#                 },
#                 {
#                     "$project": {
#                         "_id": 0,
#                         "value": "$cod",
#                         "label": {
#                             "$getField": {
#                                 "field": "nome",
#                                 "input": {"$first": "$nome"},
#                             }
#                         },
#                     }
#                 },
#             ]
#         )
#     )


# @callback(
#     Output("adm-results-vela-unidades", "data"),
#     Input("adm-results-vela-gestores", "value"),
#     prevent_initial_call=True,
# )
# def atualizar_unidades(gestores: list[str]):
#     return consultar_unidades(gestores)


# def consultar_aplicacoes(id_unidades: list[int], id_empresa: ObjectId):
#     r = db("Usuários").aggregate(
#         [
#             {
#                 "$match": {
#                     "unidades": {"$in": id_unidades},
#                     "empresa": id_empresa,
#                 }
#             },
#             {"$group": {"_id": None, "data": {"$push": "$_id"}}},
#             {
#                 "$lookup": {
#                     "from": "VelaAplicações",
#                     "let": {"usuarios": "$data"},
#                     "pipeline": [
#                         {
#                             "$set": {
#                                 "inter": {
#                                     "$setIntersection": ["$participantes", "$$usuarios"]
#                                 },
#                                 "_id": {"$toString": "$_id"},
#                             }
#                         },
#                         {"$match": {"inter.0": {"$exists": 1}}},
#                     ],
#                     "as": "aplicacoes",
#                 }
#             },
#             {"$project": {"aplicacoes": {"_id": 1, "descricao": 1}, "_id": 0}},
#         ]
#     )
#     if not r.alive:
#         return []
#     aplicacoes = r.next()["aplicacoes"]
#     return [
#         {"label": aplicacao["descricao"], "value": aplicacao["_id"]}
#         for aplicacao in aplicacoes
#     ]


# @callback(
#     Output("adm-results-vela-aplicacao", "data"),
#     Input("adm-results-vela-unidades", "value"),
#     State("adm-results-vela-empresa", "value"),
#     prevent_initial_call=True,
# )
# def atualizar_aplicacoes(id_unidades: list[str], id_empresa: str):
#     return consultar_aplicacoes(id_unidades, ObjectId(id_empresa))


# @callback(
#     Output("adm-results-vela-nota-media", "children"),
#     Output("adm-results-vela-qtd-respostas", "children"),
#     Output("adm-results-vela-qtd-aplicacoes", "children"),
#     Output("adm-results-vela-etapas", "data"),
#     Output("adm-results-vela-competencias", "data"),
#     Output("adm-results-vela-table", "columnDefs"),
#     Output("adm-results-vela-table", "rowData"),
#     Input("adm-results-vela-ok-btn", "n_clicks"),
#     State("adm-results-vela-aplicacao", "value"),
#     prevent_initial_call=True,
# )
# def atualizar_dashboard_adm_vela_resultados(n: int, ids_aplicacao: list[str]):
#     if not n:
#         raise PreventUpdate
#     if not ids_aplicacao:
#         return (
#             None,
#             None,
#             None,
#             {"datasets": [], "labels": []},
#             {"datasets": [], "labels": []},
#             [],
#             [],
#         )
#     aplicacoes = consultar_df_respostas_aplicacoes(
#         [ObjectId(id) for id in ids_aplicacao]
#     )

#     dfs = Vela.carregar_formulario()

#     df_respostas = (
#         pl.DataFrame(aplicacoes)
#         .select(pl.all().name.suffix("_aplicacao"))
#         .explode("respostas_aplicacao")
#         .unnest("respostas_aplicacao")
#         .rename({"_id": "_id_resposta"})
#         .unnest("frases")
#         .melt(
#             id_vars=[
#                 "_id_aplicacao",
#                 "descricao_aplicacao",
#                 "v_form_aplicacao",
#                 "id_usuario",
#                 "usuario",
#                 "_id_resposta",
#             ],
#             variable_name="id_frase",
#             value_name="resposta",
#         )
#         .with_columns(
#             pl.col("_id_aplicacao", "_id_resposta", "id_usuario").map_elements(
#                 lambda x: str(x), return_dtype=str
#             ),
#             pl.col("id_frase").cast(pl.Int64),
#             pl.col("usuario").list.first(),
#         )
#         .join(dfs.competencias, left_on="id_frase", right_on="id", how="left")
#         .with_columns(pl.col("notas").list.get(pl.col("resposta").sub(1)).alias("nota"))
#         .drop("resposta", "notas")
#         .rename({"nome": "competencias", "desc": "frase"})
#     )

#     df_respostas_etapas = (
#         df_respostas.join(dfs.etapas, on="competencias", how="left")
#         .rename({"nome": "etapa", "id": "id_etapa", "peso": "peso_etapa"})
#         .group_by("_id_resposta", "id_etapa")
#         .agg(pl.col("usuario").first(), pl.col("etapa").first(), pl.col("nota").mean())
#     )

#     df_notas_etapas = (
#         df_respostas_etapas.sort("id_etapa")
#         .group_by("etapa", maintain_order=True)
#         .agg(pl.col("nota").mean())
#     )
#     DATA_NOTAS_ETAPAS = {
#         "labels": df_notas_etapas.get_column("etapa").to_list(),
#         "datasets": [
#             {
#                 "label": "Nota média",
#                 "data": df_notas_etapas.get_column("nota").round(1).to_list(),
#                 "backgroundColor": "#1618ff",
#             }
#         ],
#     }

#     df_notas_competencias = (
#         df_respostas.group_by("competencias")
#         .agg(pl.col("nota").mean())
#         .with_columns(
#             pl.when(pl.col("nota").ge(8))
#             .then(pl.lit("#57b956"))
#             .when(pl.col("nota").lt(5))
#             .then(pl.lit("#d23535"))
#             .otherwise(pl.lit("#b3b3b3"))
#             .alias("cor")
#         )
#         .sort("competencias")
#     )

#     DATA_NOTAS_COMPETENCIAS = {
#         "labels": df_notas_competencias.get_column("competencias").to_list(),
#         "datasets": [
#             {
#                 "label": "Nota média",
#                 "data": df_notas_competencias.get_column("nota").round(1).to_list(),
#                 "backgroundColor": df_notas_competencias.get_column("cor").to_list(),
#                 "datalabels": {
#                     "backgroundColor": df_notas_competencias.get_column(
#                         "cor"
#                     ).to_list(),
#                 },
#                 "labels": df_notas_competencias.get_column("nota")
#                 .map_elements(lambda x: f"{x:.1f}", return_dtype=str)
#                 .to_list(),
#             }
#         ],
#     }

#     df_notas_competencias_usuarios = (
#         df_respostas.sort("competencias", "usuario")
#         .group_by("competencias", "usuario", maintain_order=True)
#         .agg(pl.col("nota").mean())
#         .pivot(values="nota", index="usuario", columns="competencias")
#         .with_columns(pl.col(pl.NUMERIC_DTYPES).round(1))
#     )

#     GRID_COLUNAS = [
#         {"field": col, "valueFormatter": {"function": "FMT(params.value)"}}
#         for col in df_notas_competencias_usuarios.columns
#     ]
#     GRID_DATA = df_notas_competencias_usuarios.to_dicts()

#     NOTA_MEDIA = (
#         df_respostas_etapas.group_by("_id_resposta")
#         .agg(pl.col("nota").sum())
#         .get_column("nota")
#         .mean()
#     )

#     QTD_RESPOSTAS = df_respostas.get_column("_id_resposta").n_unique()

#     QTD_APLICACOES = df_respostas.get_column("_id_aplicacao").n_unique()

#     return (
#         f"{NOTA_MEDIA:.1f}",
#         QTD_RESPOSTAS,
#         QTD_APLICACOES,
#         DATA_NOTAS_ETAPAS,
#         DATA_NOTAS_COMPETENCIAS,
#         GRID_COLUNAS,
#         GRID_DATA,
#     )


# def consultar_df_respostas_aplicacoes(ids_aplicacao: list[ObjectId]):
#     aplicacoes = list(
#         db("VelaAplicações").aggregate(
#             [
#                 {"$match": {"_id": {"$in": ids_aplicacao}}},
#                 {
#                     "$lookup": {
#                         "from": "VelaRespostas",
#                         "let": {"id_aplicacao": "$_id"},
#                         "pipeline": [
#                             {
#                                 "$match": {
#                                     "$expr": {
#                                         "$eq": ["$id_aplicacao", "$$id_aplicacao"]
#                                     }
#                                 }
#                             },
#                             {
#                                 "$lookup": {
#                                     "from": "Usuários",
#                                     "localField": "id_usuario",
#                                     "foreignField": "_id",
#                                     "as": "usuario",
#                                 },
#                             },
#                             {
#                                 "$set": {
#                                     "id_usuario": {"$toString": "$id_usuario"},
#                                     "_id": {"$toString": "$_id"},
#                                     "usuario": "$usuario.nome",
#                                 }
#                             },
#                         ],
#                         "localField": "_id",
#                         "foreignField": "id_aplicacao",
#                         "as": "respostas",
#                     }
#                 },
#                 {
#                     "$project": {
#                         "participantes": 0,
#                         "empresa": 0,
#                         "respostas": {
#                             "nota": 0,
#                             "id_aplicacao": 0,
#                         },
#                     }
#                 },
#             ]
#         )
#     )

#     return aplicacoes
