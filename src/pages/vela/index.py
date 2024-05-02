import dash_mantine_components as dmc
from dash import dcc, get_asset_url, html, register_page
from dash_iconify import DashIconify
from utils.modelo_assessment import VelaAssessment
from utils.modelo_usuario import Usuario, checar_perfil

register_page(
    __name__,
    path="/app/vela",
    title="Vela Assessment",
    redirect_from=["/app/dashboard"],
)


@checar_perfil
def layout():
    usr_atual = Usuario.atual()

    r = VelaAssessment.testes_disponiveis(usr_atual.id_)
    ultima_aplicacao = r["ultima_aplicacao"] if r else None
    ultima_resposta_id = r["ultima_resposta_id"] if r else None

    return html.Div(
        className="center-container",
        children=[
            dmc.Image(
                src=get_asset_url("imgs/vela/00 - VELA 1.png"),
                mb="1rem",
                width=250,
                alt="Logo Vela Assessment",
            ),
            dmc.Text(
                "Te damos as boas-vindas ao Vela Assessment.",
                weight=500,
                align="center",
                mb="4rem",
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
                        ),
                        href=f"/app/vela/teste/?id={ultima_aplicacao['id']}"
                        if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                        else None,
                    ),
                    dmc.Anchor(
                        dmc.Button(
                            children="Ver resultado",
                            disabled=not ultima_resposta_id,
                            color="BooptLaranja",
                        ),
                        href=f"/app/vela/resultado/?usr={usr_atual.id}&resposta={ultima_resposta_id}"
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
                                    href="",
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
