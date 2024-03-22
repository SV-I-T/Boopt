from random import choice, sample
from urllib.parse import parse_qs

import dash_mantine_components as dmc
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
from flask_login import current_user
from utils.banco_dados import db
from utils.modelo_usuario import Usuario, checar_login

EXPLICACAO_MD = """
    Olá **{vendedor}**!
    
    Esse mapeamento tem como objetivo analisar o quanto você tem desenvolvido as  competências essenciais para ser um vendedor de sucesso.
    
    **Escolha um local calmo e livre de interrupções** para responder esse formulário. **Você só poderá enviar uma vez**, então procure estar concentrado no exercício e responda com sinceridade, isso trará um resultado mais realista. A previsão de término é em apenas 10 minutos ⏳.

    Funciona da seguinte maneira: A seguir, teremos afirmações que devem ser classificadas de 1 a 5, onde:
    * **1 significa**: Não me identifico nada
    * **5 significa**: Me identifico muito
"""


register_page(
    __name__, path="/app/assessment-vendedor/teste", title="Assessment Vendedor"
)


@checar_login
def layout(id: str = None, secao: str = "instrucoes"):
    if id is None or len(id) != 24:
        return dmc.Alert(
            "Este formulário não existe. Verifique o link", title="Erro", color="red"
        )

    usr: Usuario = current_user

    if secao == "instrucoes":
        return html.Div(
            className="center-container",
            children=[
                dcc.Markdown(
                    EXPLICACAO_MD.format(vendedor=usr.nome),
                    style={"font-weight": 400, "font-size": 30},
                ),
                dmc.Anchor(
                    href=f"/app/assessment-vendedor/teste/?id={id}&secao=frases",
                    children=dmc.Button(
                        "Começar teste",
                        color="BooptLaranja",
                    ),
                ),
            ],
        )

    elif secao == "frases":
        aplicacao = db("AssessmentVendedores", "Aplicações").find_one(
            {"participantes": usr.id_, "_id": ObjectId(id)}
        )

        formulario_frases = db("AssessmentVendedores", "Formulários").find_one(
            {"_id": aplicacao["id_form"]},
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

        frase_atual = frases[str(ordem[0])]

        return html.Div(
            className="center-container",
            children=[
                dcc.Store(id="store-frases", data=frases, storage_type="local"),
                dcc.Store(id="store-status-done", data=False, storage_type="local"),
                dcc.Store(id="store-ordem-frases", data=ordem, storage_type="local"),
                dcc.Store(id="store-ordem-frase-atual", data=0, storage_type="local"),
                html.Div(className="progress-bar", children=[html.Div(), html.Div()]),
                dmc.Container(
                    h=400,
                    children=dmc.Text(
                        id="text-frase",
                        children=frase_atual["frase"],
                        weight=500,
                        size=18,
                        align="center",
                        display="flex",
                        h="100%",
                        style={"align-items": "center"},
                    ),
                ),
                dmc.Group(
                    align="center",
                    position="center",
                    children=[
                        dmc.Text(
                            "Não me identifico",
                            color="BooptLaranja",
                            size=16,
                            weight=700,
                        ),
                        dcc.RadioItems(
                            id="nota-av",
                            className="radio-notas-frase",
                            options=[
                                {"value": i, "label": ""}
                                for i in ["1", "2", "3", "4", "5"]
                            ],
                            inline=True,
                            value=None,
                        ),
                        dmc.Text(
                            "Me identifico muito", color="SVAzul", size=16, weight=700
                        ),
                    ],
                ),
                dmc.Group(
                    my="5rem",
                    position="center",
                    children=[
                        dmc.Button(
                            "Anterior",
                            leftIcon=DashIconify(icon="bxs:left-arrow"),
                            id="btn-back",
                            disabled=True,
                            color="dark",
                        ),
                        dmc.Button(
                            "Próximo",
                            rightIcon=DashIconify(icon="bxs:right-arrow"),
                            color="dark",
                            id="btn-next",
                        ),
                        dmc.Button("Auto-preencher", id="btn-last"),
                    ],
                ),
                html.Div(id="container-envio"),
            ],
        )
    elif secao == "enviado":
        return [
            dmc.Title("Obrigado!"),
            dmc.Text(
                [
                    "Você pode conferir seu resultado agora mesmo clicando ",
                    dmc.Anchor("aqui", href="/app/assessment-vendedor", underline=True),
                ]
            ),
        ]


# CALLBACK PARA PREENCHER TODAS AS FRASES AUTOMATICAMENTE
@callback(
    Output("store-frases", "data", allow_duplicate=True),
    Output("store-ordem-frase-atual", "data", allow_duplicate=True),
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
        return frases, 62


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
    Output("nota-av", "value"),
    Output("btn-next", "disabled"),
    Output("btn-back", "disabled"),
    Input("store-ordem-frase-atual", "data"),
    State("store-frases", "data"),
    State("store-ordem-frases", "data"),
)

# ATUALIZA O VALOR DA FRASE QUANDO CLICA NUMA NOTA
clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="nota_clicada"),
    Output("store-frases", "data"),
    Input("nota-av", "value"),
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
            bg="#D9D9D9",
            px="1rem",
            children=dmc.Group(
                position="apart",
                children=[
                    html.Div(
                        [
                            dmc.Text("Tudo pronto!", weight=700, color="SVAzul"),
                            dmc.Text(
                                "Você pode revisar suas respostas ou enviá-las agora mesmo.",
                                weight=400,
                            ),
                        ]
                    ),
                    dmc.Button(
                        id="btn-enviar",
                        children="Enviar",
                        variant="gradient",
                    ),
                ],
            ),
        )


@callback(
    Output("url", "search", allow_duplicate=True),
    Output("notificacoes", "children", allow_duplicate=True),
    Input("btn-enviar", "n_clicks"),
    State("store-frases", "data"),
    State("url", "search"),
    prevent_initial_call=True,
)
def salvar_resposta(n, frases, search):
    if not n or callback_context.triggered_id != "btn-enviar":
        raise PreventUpdate

    else:
        usr_atual: Usuario = current_user
        params = parse_qs(search[1:])
        id_aplicacao = params["id"][0]
        dados_resposta = {
            "notas": [
                {"id": int(k), "nota": int(v["valor"])} for k, v in frases.items()
            ],
            "id_aplicacao": ObjectId(id_aplicacao),
            "id_usuario": usr_atual.id_,
        }
        resposta = db("AssessmentVendedores", "Respostas").insert_one(dados_resposta)
        if resposta.inserted_id:
            return f"?id={id_aplicacao}&secao=enviado", no_update
        else:
            return no_update, dmc.Notification(
                id="erro-envio-teste",
                color="red",
                title="Atenção",
                message="Erro ao salvar resposta. Tente novamente",
                action="show",
            )
