import dash_mantine_components as dmc
from dash import dcc, get_asset_url, html, register_page
from dash_iconify import DashIconify

from utils.login import checar_perfil
from utils.usuario import Usuario
from utils.vela import Vela

register_page(
    __name__,
    path="/app/vela",
    title="Vela Assessment",
    redirect_from=["/app/dashboard"],
)


@checar_perfil
def layout():
    return dmc.Stack(
        children=[
            html.Div(
                className="index-vela-promo",
                children=[
                    html.Img(
                        src=get_asset_url("assets/vela/vela-mar.jpg"),
                        alt="Barco",
                        className="barco",
                    ),
                    html.Img(
                        src=get_asset_url("assets/vela/tag_ass_inv.svg"),
                        alt="Logo Vela Assessment",
                        className="logo",
                    ),
                ],
            ),
            html.Div(
                [
                    html.H2("Bem-vindo ao seu mapeamento de competências!"),
                    html.P(
                        "Este é um passo importante para entender como você está se saindo nas habilidades cruciais para o sucesso nas vendas."
                    ),
                ]
            ),
            *controles_vela(),
        ],
    )


def controles_vela():
    usr_atual = Usuario.atual()
    r = Vela.testes_disponiveis(usr_atual.id_)
    ultima_aplicacao = r["ultima_aplicacao"] if r else None
    ultima_resposta_id = r["ultima_resposta_id"] if r else None

    controles = []

    if ultima_aplicacao and not ultima_aplicacao.get("resposta"):
        controles.append(card_teste_disponivel(ultima_aplicacao))
    if not ultima_resposta_id:
        controles.append(card_teste_indisponivel())
    else:
        controles.append(botao_ver_resultado(ultima_resposta_id, usr_atual))

    return controles


def card_teste_disponivel(ultima_aplicacao):
    return html.Div(
        className="card",
        children=dmc.Stack(
            [
                html.H2("Você tem um teste disponível!"),
                html.P(
                    "Antes de começar, procure um lugar tranquilo onde você não será interrompido. Isso ajuda a garantir que você se concentre totalmente e responda da forma mais precisa."
                ),
                dmc.Anchor(
                    dmc.Button(
                        children="Ir para o teste",
                    ),
                    href=f"/app/vela/teste/{ultima_aplicacao['id']}",
                ),
            ]
        ),
    )


def card_teste_indisponivel():
    return html.Div(
        className="card",
        children=html.H2(
            "Você ainda não foi cadastrado para um teste Vela. Verifique com o seu RH."
        ),
    )


def botao_ver_resultado(ultima_resposta_id, usr_atual: Usuario):
    return dmc.Anchor(
        dmc.Button(
            children="Ver meu resultado",
            classNames={"root": "btn-vela"},
            leftIcon=DashIconify(icon="fluent:chart-multiple-20-regular", width=20),
        ),
        href=f"/app/vela/report/{usr_atual.id}/{ultima_resposta_id}",
        underline=False,
    )
