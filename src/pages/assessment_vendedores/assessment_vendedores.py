import re
from random import choice, sample

import dash_mantine_components as dmc
import pendulum
from bson import ObjectId
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    callback_context,
    clientside_callback,
    dcc,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from icecream import ic  # noqa: F401
from utils.banco_dados import mongo

from .funcoes.cpf import layout_cpf

explicacao_teste = dcc.Markdown(
    """
    Olá Vendedor!
    
    Esse mapeamento tem como objetivo analisar o quanto você tem desenvolvido as  competências essenciais para ser um vendedor de sucesso.
    
    **Escolha um local calmo e livre de interrupções** para responder esse formulário. **Você só poderá enviar uma vez**, então procure estar concentrado no exercício e responda com sinceridade, isso trará um resultado mais realista. A previsão de término é em apenas 10 minutos ⏳.

    Funciona da seguinte maneira: A seguir, teremos afirmações que devem ser classificadas de 1 a 5, onde:
    * **1 significa**: Não me identifico nada
    * **5 significa**: Me identifico muito
"""
)

register_page(
    __name__, path="/assessment-vendedor/assessment", title="Assessment Vendedor"
)


def layout(id: str = None, cpf: str = None):
    if id is None or len(id) != 24:
        return dmc.Alert(
            "Este formulário não existe. Verifique o link", title="Erro", color="red"
        )

    if cpf is None:
        return layout_cpf

    elif len(id) != 0 and cpf is not None:
        aplicacao = buscar_aplicacao(cpf, id)

        if aplicacao is None:
            return dmc.Alert(
                [
                    dmc.Text(
                        f"O cpf '{cpf}' não foi registrado para essa aplicação ou ela não existe."
                    ),
                    dmc.Anchor("Voltar", href=f"/assessment-vendedor?id={id}"),
                ],
                title="Erro!",
                color="red",
            )

        aplicacao = aplicacao[0]
        id_form = aplicacao["id_form"]
        nome = aplicacao["participantes"]["Nome"]
        cliente = aplicacao["cliente"]

        if "resposta" in aplicacao.keys():
            # ADICIONAR O NOME/DATA DA APLICAÇÃO
            return dmc.Alert(
                f"O CPF {cpf} já respondeu esta aplicação.", color="yellow"
            )

        formulario_frases = mongo.cx["AssessmentVendedores"]["Formulários"].find_one(
            {"_id": id_form},
            {
                "_id": 0,
                "competencias.frases.desc": 1,
                "competencias.frases.id": 1,
            },
        )

        frases = {
            str(frase["id"]): {"frase": frase["desc"], "valor": None}
            for competencia in formulario_frases["competencias"]
            for frase in competencia["frases"]
        }

        ordem = sample(range(1, 63 + 1), 63)

        return html.Div(
            [
                dcc.Store(id="store-status-start", data=False, storage_type="memory"),
                dcc.Store(id="store-status-done", data=False, storage_type="memory"),
                dcc.Store(id="store-frases", data=frases, storage_type="memory"),
                dcc.Store(id="store-ordem-frases", data=ordem, storage_type="memory"),
                dcc.Store(
                    id="store-ordem-frase-atual", data=None, storage_type="memory"
                ),
                dmc.Text(f"{nome} - {cliente}", size="sm", color="grey"),
                html.Div(id="container-frase"),
                dmc.Grid(
                    [
                        dmc.Col(
                            dmc.Button("Começar teste", id="btn-start"),
                            span="auto",
                        ),
                    ],
                    mt="1rem",
                    id="group-btn",
                    align="center",
                    gutter="sm",
                ),
                # dmc.Button("Ultima", id="btn-last"),
                html.Div(id="container-envio"),
            ],
            id="container-teste",
        )


# CALLBACK PARA PREENCHER TODAS AS FRASES AUTOMATICAMENTE
@callback(
    Output("store-ordem-frase-atual", "data", allow_duplicate=True),
    Output("store-frases", "data", allow_duplicate=True),
    Input("btn-last", "n_clicks"),
    State("store-frases", "data"),
    prevent_initial_call=True,
)
def preencher_auto(n, frases):
    if not n:
        raise PreventUpdate
    else:
        for k in frases:
            frases[k]["valor"] = choice([1, 2, 3, 4, 5])
        return 62, frases


# INICIA O TESTE AO CLICAR NO BOTÃO DE INICIAR
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="iniciar_teste"),
    Output("store-status-start", "data"),
    Output("store-ordem-frase-atual", "data"),
    Input("btn-start", "n_clicks"),
    prevent_initial_call=True,
)


# CRIA O CONTAINER DAS PERGUNTAS AO MUDAR O STATUS DE INÍCIO
@callback(
    Output("container-frase", "children"),
    Output("group-btn", "children"),
    Input("store-status-start", "data"),
    State("container-teste", "children"),
    State("store-ordem-frase-atual", "data"),
    State("store-frases", "data"),
    State("store-ordem-frases", "data"),
)
def atualizar_container_frase(status_comecou, _, ordem_atual, frases, ordem):
    if not status_comecou:
        return [
            explicacao_teste,
        ], no_update
    else:
        frase_atual = frases[str(ordem[ordem_atual])]
        return [
            dmc.Text(
                frase_atual["frase"],
                id="text-frase",
                style={"height": 130},
                weight=700,
                size="lg",
            ),
            dmc.Stack(
                [
                    dmc.SegmentedControl(
                        [str(n) for n in range(1, 6)],
                        value=frase_atual["valor"],
                        id="btn-notas-frase",
                        size="xl",
                        color="theme.colors.primaryColor",
                    ),
                    dmc.Grid(
                        [
                            dmc.Col(
                                dmc.Text(
                                    "Não me identifico nada",
                                    size="sm",
                                    color="grey",
                                    align="left",
                                ),
                                span="content",
                                p=0,
                            ),
                            dmc.Col(
                                dmc.Text(
                                    "Me identifico muito",
                                    size="sm",
                                    color="grey",
                                    align="right",
                                ),
                                span="content",
                                p=0,
                            ),
                        ],
                        justify="space-between",
                        p=0,
                    ),
                ],
                align="stretch",
                justify="center",
                spacing="sm",
                pb="1rem",
            ),
        ], [
            dmc.Col(
                dmc.Button(
                    DashIconify(icon="bxs:left-arrow"),
                    n_clicks=0,
                    id="btn-back",
                    disabled=True,
                    color="gray",
                    px=10,
                    variant="outline",
                ),
                span="content",
                p=5,
            ),
            dmc.Col(
                dmc.Button(
                    "Próximo",
                    rightIcon=DashIconify(icon="bxs:right-arrow"),
                    n_clicks=0,
                    id="btn-next",
                ),
                span="content",
                p=0,
            ),
            dmc.Col(
                dmc.Progress(id="progress-bar", size="xl", striped=True), span="auto"
            ),
            dmc.Col(dmc.Text(id="progress-text"), span="content"),
            dmc.Col(
                dmc.Button("Auto-preencher", id="btn-last", variant="subtle"),
                span="content",
                p=0,
            ),
        ]


# ALTERA A FRASE ATUAL SEGUNDO OS BOTÕES
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="alterar_frase"),
    Output("store-ordem-frase-atual", "data", allow_duplicate=True),
    Input("btn-next", "n_clicks"),
    Input("btn-back", "n_clicks"),
    State("store-ordem-frase-atual", "data"),
    prevent_initial_call=True,
)

# ATUALIZA COMPONENTES SEGUNDO A FRASE ATUAL
clientside_callback(
    ClientsideFunction(
        namespace="clientside", function_name="atualizar_componentes_frase"
    ),
    Output("text-frase", "children"),
    Output("btn-notas-frase", "value"),
    Output("btn-next", "disabled"),
    Output("btn-back", "disabled"),
    Output("progress-bar", "value"),
    Output("progress-text", "children"),
    Input("store-ordem-frase-atual", "data"),
    State("store-frases", "data"),
    State("store-ordem-frases", "data"),
)

# ATUALIZA O VALOR DA FRASE QUANDO CLICA NUMA NOTA
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="nota_clicada"),
    Output("store-frases", "data"),
    Input("btn-notas-frase", "value"),
    State("store-ordem-frase-atual", "data"),
    State("store-ordem-frases", "data"),
    State("store-frases", "data"),
    prevent_initial_call=True,
)

# VERIFICA SE TODAS AS FRASES JÁ FORAM RESPONDIDAS
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="check_completado"),
    Output("store-status-done", "data"),
    Input("store-frases", "data"),
)


# SE TODAS FRASES FORAM RESPONDIDAS, HABILITA O ENVIO
@callback(
    Output("container-envio", "children"),
    Input("store-status-done", "data"),
    prevent_initial_call=True,
)
def habilitar_envio(status_pronto):
    if not status_pronto:
        raise PreventUpdate
    else:
        return dmc.Alert(
            [
                dmc.Text("Você pode revisar suas respostas ou enviá-las agora mesmo."),
                dmc.Button("Enviar", color="green", id="btn-enviar", mt="0.5rem"),
            ],
            title="Tudo pronto!",
            color="green",
            mt="0.5rem",
        )


def buscar_aplicacao(cpf, id):
    return list(
        mongo.cx["AssessmentVendedores"]["Aplicações"].aggregate(
            [
                {"$unwind": "$participantes"},
                {"$match": {"participantes.CPF": cpf, "_id": ObjectId(id)}},
                {"$limit": 1},
                {"$unwind": "$participantes"},
                {
                    "$lookup": {
                        "from": "Respostas",
                        "let": {"cpf": cpf, "id": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$cpf", "$$cpf"]},
                                            {"$eq": ["$id_aplicacao", "$$id"]},
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "resposta",
                    }
                },
                {"$unwind": {"path": "$resposta", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "id_form": 1,
                        "participantes": {"Nome": 1},
                        "cliente": 1,
                        "_id": 0,
                        "resposta": {"_id": 1},
                    }
                },
            ]
        )
    )


@callback(
    Output("container-frase", "children", allow_duplicate=True),
    Output("group-btn", "children", allow_duplicate=True),
    Output("container-envio", "children", allow_duplicate=True),
    Input("btn-enviar", "n_clicks"),
    State("store-frases", "data"),
    State("url", "search"),
    prevent_initial_call=True,
)
def salvar_resposta(n, frases, search):
    if not n or callback_context.triggered_id != "btn-enviar":
        raise PreventUpdate

    else:
        id = re.search("id\=([a-zA-Z0-9]*)\&?", search).group(1)
        cpf = re.search("cpf\=([0-9]{11})\&?", search).group(1)
        dt = pendulum.now("America/Sao_Paulo")
        tb_respostas = mongo.cx["AssessmentVendedores"]["Respostas"]
        dados_resposta = {
            "notas": [
                {"id": int(k), "nota": int(v["valor"])} for k, v in frases.items()
            ],
            "dt": dt,
            "cpf": cpf,
            "id_aplicacao": ObjectId(id),
        }
        resposta = tb_respostas.insert_one(dados_resposta)
        if resposta.inserted_id is not None:
            return (
                [
                    dmc.Title("Obrigado!"),
                    dmc.Text(
                        [
                            "Sua resposta foi enviada. Você pode conferir a avaliação da sua resposta ",
                            dmc.Anchor(
                                "aqui",
                                href=f"/assessment-vendedor/resultados?cpf={cpf}",
                            ),
                            ".",
                        ]
                    ),
                ],
                None,
                None,
            )
        else:
            raise PreventUpdate
