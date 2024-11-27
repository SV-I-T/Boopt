from random import choice, shuffle

import dash_mantine_components as dmc
import polars as pl
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
    get_asset_url,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from utils import Usuario, Vela, checar_perfil, db, nova_notificacao

register_page(
    __name__,
    path_template="/app/vela/teste/<id_aplicacao>/",
    title="Vela Assessment - Teste",
)


@checar_perfil
def layout(id_aplicacao: str = None, secao: str = "instrucoes", **kwargs):
    if id_aplicacao is None or len(id_aplicacao) != 24:
        return dmc.Alert(
            "Este formulário não existe. Verifique o link", title="Erro", color="red"
        )

    usr = Usuario.atual()

    if secao == "instrucoes":
        return dmc.Stack(
            spacing="2rem",
            children=[
                dmc.Group(
                    children=[
                        html.Img(
                            src=get_asset_url("assets/vela/logo.svg"),
                            height=90,
                            alt="Logo Vela",
                        ),
                        dcc.Markdown(
                            f"Olá **{usr.primeiro_nome}**,", className="vela-saudacao"
                        ),
                        html.Div(
                            children=[html.Div()] * 3,
                            className="vela-circles",
                        ),
                    ]
                ),
                html.P(
                    "A sinceridade é fundamental aqui. Responder com honestidade não só nos dará uma visão mais clara de onde você está, mas também como podemos ajudá-lo a crescer."
                ),
                html.P(
                    "Não se preocupe, todo o processo será rápido - cerca de 20 minutos do seu tempo."
                ),
                html.P(
                    [
                        "Aqui está como funiona: Você encontrará afirmações que precisam ser avaliadas em uma escala de ",
                        html.Strong("Discordo totalmente"),
                        " a ",
                        html.Strong("Concordo totalmente."),
                    ]
                ),
                html.Div(
                    className="vela-radio",
                    children=[
                        html.P(
                            "Discordo totalmente",
                            className="label-teste",
                        ),
                        html.Div(className="vela-nota-demo", children=[html.Div()] * 5),
                        html.P(
                            "Concordo totalmente",
                            className="label-teste",
                        ),
                    ],
                ),
                html.P(
                    "Após finalizar o teste você será redirecionado para a página inicial do Vela, onde poderá ver seu resultado."
                ),
                html.Strong(
                    "Atenção: você não poderá refazer esse teste novamente durante seis meses."
                ),
                html.Div(
                    className="card",
                    children=dmc.Group(
                        position="apart",
                        children=[
                            html.Div(
                                children=[
                                    html.H2("Vamos lá?"),
                                    html.P(
                                        "Sua jornada de autoavaliação está prestes a partir.",
                                    ),
                                ],
                            ),
                            dmc.Anchor(
                                href=f"/app/vela/teste/{id_aplicacao}/?secao=frases",
                                children=dmc.Button("Estou pronto"),
                            ),
                        ],
                    ),
                ),
            ],
        )

    elif secao == "frases":
        aplicacao = db("VelaAplicações").find_one(
            {"participantes": usr.id_, "_id": ObjectId(id_aplicacao)}
        )

        df_competencias = Vela.carregar_formulario(
            v_form=aplicacao["v_form"]
        ).competencias

        frases = {
            str(frase["id"]): {"frase": frase["desc"], "valor": None}
            for frase in df_competencias.iter_rows(named=True)
        }

        ordem = list(frases.keys())
        shuffle(ordem)

        frase_atual = frases[str(ordem[0])]

        return dmc.Stack(
            className="center-container test-vela",
            children=[
                dcc.Store(
                    id="store-id-aplicacao-vela",
                    data=id_aplicacao,
                    storage_type="memory",
                ),
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
                    className="vela-radio",
                    children=[
                        html.P(
                            "Discordo totalmente",
                            className="label-teste",
                        ),
                        dcc.RadioItems(
                            id="score-vela",
                            className="vela-nota",
                            options=[
                                {"value": i, "label": ""}
                                for i in ["1", "2", "3", "4", "5"]
                            ],
                            inline=True,
                            value=None,
                        ),
                        html.P(
                            "Concordo totalmente",
                            className="label-teste",
                        ),
                    ],
                ),
                dmc.Group(
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
    ClientsideFunction(namespace="vela", function_name="alterar_frase"),
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
    ClientsideFunction(namespace="vela", function_name="nota_clicada"),
    Output("store-frases-vela", "data"),
    Input("score-vela", "value"),
    State("store-frase-atual-vela", "data"),
    State("store-ordem-vela", "data"),
    State("store-frases-vela", "data"),
    prevent_initial_call=True,
)

# VERIFICA SE TODAS AS FRASES JÁ FORAM RESPONDIDAS
clientside_callback(
    ClientsideFunction(namespace="vela", function_name="check_completado"),
    Output("store-status-vela", "data"),
    Input("store-frases-vela", "data"),
)


# SE TODAS FRASES FORAM RESPONDIDAS, HABILITA O ENVIO
@callback(
    Output("send-container-vela", "children"),
    Input("store-status-vela", "data"),
    State("store-id-aplicacao-vela", "data"),
    prevent_initial_call=True,
)
def habilitar_envio(status_pronto, id_aplicacao):
    if not status_pronto:
        raise PreventUpdate
    else:
        return html.Div(
            className="card",
            children=dmc.Group(
                position="apart",
                children=[
                    html.Div(
                        children=[
                            html.H2("Tudo pronto!"),
                            html.P(
                                "Você pode revisar suas respostas ou enviá-las agora mesmo."
                            ),
                        ],
                    ),
                    dmc.Button(
                        id="btn-enviar",
                        children="Enviar",
                    ),
                ],
            ),
        )


# ENVIAR RESPOSTA
@callback(
    Output("url", "href", allow_duplicate=True),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-enviar", "n_clicks"),
    State("store-frases-vela", "data"),
    State("store-id-aplicacao-vela", "data"),
    prevent_initial_call=True,
)
def salvar_resposta(n, frases, id_aplicacao):
    if not n or callback_context.triggered_id != "btn-enviar":
        raise PreventUpdate

    else:
        usr_atual = Usuario.atual()
        dados_resposta = {
            "frases": {k: int(v["valor"]) for k, v in frases.items()},
            "id_aplicacao": ObjectId(id_aplicacao),
            "id_usuario": usr_atual.id_,
        }

        dados_resposta["nota"] = calcular_nota(id_aplicacao, dados_resposta["frases"])

        resposta = db("VelaRespostas").insert_one(dados_resposta)

        if resposta.inserted_id:
            # if True:
            return "/app/vela", nova_notificacao(
                id="envio-teste",
                type="success",
                message='Obrigado! Você poderá ver seu relatório clicando em "Ver meu resultado"',
            )
        else:
            return no_update, nova_notificacao(
                id="erro-envio-teste",
                type="error",
                message="Erro ao salvar resposta. Tente novamente",
            )


def calcular_nota(id_aplicacao: str, frases: dict[str, int]):
    dfs = Vela.carregar_formulario()
    df_competencias, df_etapas = dfs.competencias, dfs.etapas

    nota = (
        pl.DataFrame(
            list(frases.items()), schema={"id": str, "nota": int}, orient="row"
        )
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
