from random import choice, sample

import dash_mantine_components as dmc
import polars as pl
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    callback_context,
    clientside_callback,
    dcc,
    get_asset_url,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils.banco_dados import db
from utils.query import QParams
from utils.vela import Vela

EXPLICACAO_MD = """
    Bem-vindo ao seu mapeamento de competências! Este é um passo importante para entender como você está se saindo nas habilidades cruciais para o sucesso nas vendas.

    Antes de começar, procure um lugar tranquilo onde você não será interrompido. Isso ajuda a garantir que você se concentre totalmente e responda da forma mais precisa.

    A sinceridade é fundamental aqui. Responder com honestidade não só nos dará uma visão mais clara de onde você está, mas também como podemos ajudá-lo a crescer.

    **Não se preocupe, todo o processo será rápido - cerca de 20 minutos do seu tempo.**

    Aqui está como funciona: Você encontrará afirmações que precisam ser avaliadas em uma escala de **Discordo totalmente** a **Concordo totalmente**.
"""


register_page(
    __name__,
    path_template="/test/",
    title="[DEMO] Vela Assessment",
)


def layout(
    secao: str = "instrucoes",
    nome: str = "Vendedor",
    **kwargs,
):
    params_string = f"{nome=}" + "&".join([f"{k}={v}" for k, v in kwargs.items()])
    if secao == "instrucoes":
        return html.Div(
            style={
                "display": "flex",
                "flex-direction": "column",
                "height": "100%",
                "margin-top": "7rem",
            },
            children=[
                dmc.Group(
                    children=[
                        html.Img(
                            src=get_asset_url("imgs/vela/logo.svg"),
                            height=90,
                            alt="Logo Vela",
                        ),
                        dcc.Markdown(
                            f"Olá **{nome.split(' ',1)[0]}**,",
                            className="vela-saudacao",
                        ),
                        html.Div(
                            children=[html.Div()] * 3,
                            className="vela-circles",
                        ),
                    ]
                ),
                dcc.Markdown(
                    EXPLICACAO_MD,
                ),
                html.Div(
                    style={"width": 350, "align-self": "center", "margin": "2rem"},
                    children=[
                        html.Div(className="vela-nota-demo", children=[html.Div()] * 5),
                        html.Div(
                            className="labels-teste",
                            children=[
                                html.P(
                                    "Discordo totalmente",
                                    className="label-teste",
                                ),
                                html.P(
                                    "Concordo totalmente",
                                    className="label-teste",
                                ),
                            ],
                        ),
                    ],
                ),
                dmc.Group(
                    style={"margin-top": "auto", "margin-bottom": "2rem"},
                    position="apart",
                    children=[
                        dmc.Stack(
                            spacing=0,
                            children=[
                                dmc.Text("Pronto para começar?", weight=700, size=40),
                                dmc.Text(
                                    "Vamos lá, sua jornada de autoavaliação está prestes a começar.",
                                ),
                            ],
                        ),
                        dmc.Anchor(
                            href=f"/test/?secao=frases&{params_string}",
                            children=dmc.Button(
                                "Iniciar o teste",
                                classNames={"root": "btn-vela"},
                                className="btn-vela-iniciar shadow",
                            ),
                        ),
                    ],
                ),
            ],
        )

    elif secao == "frases":
        df_competencias = Vela.carregar_formulario(v_form=1).competencias

        frases = {
            str(frase["id"]): {"frase": frase["desc"], "valor": None}
            for frase in df_competencias.iter_rows(named=True)
        }

        ordem = sample(range(1, len(frases) + 1), len(frases))

        frase_atual = frases[str(ordem[0])]

        return html.Div(
            className="center-container test-vela",
            style={"margin-top": "7rem"},
            children=[
                dcc.Store(id="store-frases-vela", data=frases, storage_type="memory"),
                dcc.Store(id="store-status-vela", data=False, storage_type="memory"),
                dcc.Store(id="store-ordem-vela", data=ordem, storage_type="memory"),
                dcc.Store(id="store-frase-atual-vela", data=0, storage_type="memory"),
                html.Div(className="progress-bar", children=[html.Div(), html.Div()]),
                html.P(
                    id="text-frase-vela",
                    children=frase_atual["frase"],
                ),
                html.Div(
                    style={"width": 350},
                    children=[
                        dcc.RadioItems(
                            id="score-vela",
                            className="radio-score-vela",
                            options=[
                                {"value": i, "label": ""}
                                for i in ["1", "2", "3", "4", "5"]
                            ],
                            inline=True,
                            value=None,
                        ),
                        html.Div(
                            className="labels-teste",
                            children=[
                                html.P(
                                    "Discordo totalmente",
                                    className="label-teste",
                                ),
                                html.P(
                                    "Concordo totalmente",
                                    className="label-teste",
                                ),
                            ],
                        ),
                    ],
                ),
                dmc.Group(
                    mb="1rem",
                    position="center",
                    children=[
                        dmc.Button(
                            "Anterior",
                            leftIcon=DashIconify(
                                icon="fluent:chevron-left-20-filled", width=18
                            ),
                            id="btn-back-vela",
                            disabled=True,
                            color="dark",
                        ),
                        dmc.Button(
                            "Próximo",
                            rightIcon=DashIconify(
                                icon="fluent:chevron-right-20-filled", width=18
                            ),
                            color="dark",
                            id="btn-next-vela",
                        ),
                        dmc.ActionIcon(
                            DashIconify(
                                icon="fluent:arrow-shuffle-16-filled", width=16
                            ),
                            id="btn-last-vela",
                        ),
                    ],
                ),
                html.Div(id="send-container-vela"),
            ],
        )


# CALLBACK PARA PREENCHER TODAS AS FRASES AUTOMATICAMENTE
@callback(
    Output("store-frases-vela", "data", allow_duplicate=True),
    Input("btn-last-vela", "n_clicks"),
    State("store-frases-vela", "data"),
    prevent_initial_call=True,
)
def preencher_auto(n, frases):
    if not n:
        raise PreventUpdate
    else:
        for k in frases:
            frases[k]["valor"] = choice(["1", "2", "3", "4", "5"])
        return frases


# ALTERA A FRASE ATUAL SEGUNDO OS BOTÕES
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="alterar_frase"),
    Output("store-frase-atual-vela", "data"),
    Output("text-frase-vela", "children"),
    Output("score-vela", "value"),
    Output("btn-next-vela", "disabled"),
    Output("btn-back-vela", "disabled"),
    Input("btn-next-vela", "n_clicks"),
    Input("btn-back-vela", "n_clicks"),
    State("store-frase-atual-vela", "data"),
    State("store-frases-vela", "data"),
    State("store-ordem-vela", "data"),
)

# ATUALIZA O VALOR DA FRASE QUANDO CLICA NUMA NOTA
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="nota_clicada"),
    Output("store-frases-vela", "data"),
    Input("score-vela", "value"),
    State("store-frase-atual-vela", "data"),
    State("store-ordem-vela", "data"),
    State("store-frases-vela", "data"),
    prevent_initial_call=True,
)

# VERIFICA SE TODAS AS FRASES JÁ FORAM RESPONDIDAS
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="check_completado"),
    Output("store-status-vela", "data"),
    Input("store-frases-vela", "data"),
)


# SE TODAS FRASES FORAM RESPONDIDAS, HABILITA O ENVIO
@callback(
    Output("send-container-vela", "children"),
    Input("store-status-vela", "data"),
    State("url", "search"),
    prevent_initial_call=True,
)
def habilitar_envio(status_pronto, search: str):
    if not status_pronto:
        raise PreventUpdate
    else:
        return dmc.Group(
            style={"margin-top": "auto", "flex-wrap": "nowrap"},
            position="apart",
            children=[
                dmc.Stack(
                    spacing=0,
                    children=[
                        dmc.Text("Tudo pronto!", weight=700, size=40),
                        dmc.Text(
                            "Você pode revisar suas respostas ou enviá-las agora mesmo.",
                        ),
                    ],
                ),
                dmc.Button(
                    id="btn-enviar",
                    children="Enviar",
                    classNames={"root": "btn-vela"},
                ),
            ],
        )


# ENVIAR RESPOSTA
@callback(
    Output("url", "href", allow_duplicate=True),
    Input("btn-enviar", "n_clicks"),
    State("store-frases-vela", "data"),
    State("url", "search"),
    prevent_initial_call=True,
)
def salvar_resposta(n: int | None, frases: dict, search: str):
    if not n or callback_context.triggered_id != "btn-enviar":
        raise PreventUpdate

    else:
        params = QParams.extrair_params(search)
        dados_resposta = {
            "frases": {k: int(v["valor"]) for k, v in frases.items()},
            "usuario": params.get("nome"),
            "empresa": params.get("empresa"),
            "cargo": params.get("cargo"),
            "telefone": params.get("telefone"),
            "email": params.get("email"),
        }

        dados_resposta["nota"] = calcular_nota(dados_resposta["frases"])

        resposta = db("Respostas").insert_one(dados_resposta)

        return f"/results/{resposta.inserted_id}"


def calcular_nota(frases: dict[str, int]):
    dfs = Vela.carregar_formulario()
    df_competencias, df_etapas = dfs.competencias, dfs.etapas

    nota = (
        pl.DataFrame(list(frases.items()), schema={"id": str, "nota": int})
        .with_columns(pl.col("id").cast(pl.Int64))
        .join(df_competencias, on="id", how="left")
        .select(
            pl.col("nome").alias("competencias"),
            pl.col("notas").list.get(pl.col("nota").sub(1)).alias("pontos"),
        )
        .join(df_etapas, on="competencias", how="left")
        .group_by("nome")
        .agg(pl.col("pontos").mean())
        .get_column("pontos")
        .sum()
    )
    return nota
