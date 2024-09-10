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
    usr_atual = Usuario.atual()

    r = Vela.testes_disponiveis(usr_atual.id_)
    ultima_aplicacao = r["ultima_aplicacao"] if r else None
    ultima_resposta_id = r["ultima_resposta_id"] if r else None

    return html.Div(
        className="center-container index-vela",
        children=[
            dmc.Text("Seja bem-vindo ao", weight=300),
            dmc.Text("Assessment Vendedor Boopt.", weight=700),
            dmc.Image(
                src=get_asset_url("assets/vela/promo-vela.png"),
                mb="1rem",
                alt="Logo Vela Assessment",
            ),
            dmc.Group(
                mb="4rem",
                children=[
                    dmc.Anchor(
                        dmc.Button(
                            children="Começar o teste"
                            if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                            else "Sem teste disponível",
                            disabled=not (
                                ultima_aplicacao
                                and not ultima_aplicacao.get("resposta")
                            ),
                            classNames={"root": "btn-vela"},
                        ),
                        href=f"/app/vela/teste/{ultima_aplicacao['id']}"
                        if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                        else None,
                    ),
                    dmc.Anchor(
                        dmc.Button(
                            children="Ver resultado",
                            disabled=not ultima_resposta_id,
                            color="BooptLaranja",
                        ),
                        href=f"/app/vela/report/{usr_atual.id}/{ultima_resposta_id}"
                        if ultima_resposta_id
                        else None,
                    ),
                ],
            ),
            html.Div(
                className="card card-videos-av",
                children=dmc.Group(
                    spacing="xl",
                    children=[
                        DashIconify(
                            icon="fluent:play-48-filled",
                            color="#fff",
                            className="play-videos-av",
                        ),
                        html.Div(
                            children=[
                                dcc.Markdown(
                                    "Acesse a nossa plataforma de vídeos **após realizar o teste do Assessment Boopt**"
                                ),
                                dmc.Anchor(
                                    href="/app/vela/videos",
                                    children=dmc.Button(
                                        children="Acessar",
                                        leftIcon=DashIconify(
                                            icon="fluent:filmstrip-play-16-regular",
                                            width=16,
                                        ),
                                        className="btn-borda-gradiente",
                                        disabled=not ultima_resposta_id,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
