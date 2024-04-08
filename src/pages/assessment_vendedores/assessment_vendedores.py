import dash_mantine_components as dmc
from dash import dcc, html, register_page
from dash_iconify import DashIconify
from flask_login import current_user
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Usuario, checar_perfil

register_page(
    __name__,
    path="/app/assessment-vendedor",
    title="Assessment Vendedor",
    redirect_from=["/app/dashboard"],
)


@checar_perfil
def layout():
    usr_atual: Usuario = current_user

    r = AssessmentVendedor.testes_disponiveis(usr_atual.id_)
    ultima_aplicacao = r.get("ultima_aplicacao", None)
    ultima_resposta_id = r.get("ultima_resposta_id", None)

    return html.Div(
        className="center-container",
        children=[
            dmc.Text(
                "Bem-vindo ao Assessment de Vendedor",
                size=40,
                weight=600,
                align="center",
                mb="1rem",
            ),
            dmc.Text(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent ligula arcu, auctor vel tellus vitae, aliquam dignissim quam.",
                weight=500,
                align="center",
                mb="4rem",
            ),
            dmc.Group(
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
                            color="BooptLaranja",
                        ),
                        href=f"/app/assessment-vendedor/teste/?id={ultima_aplicacao['id']}"
                        if ultima_aplicacao and not ultima_aplicacao.get("resposta")
                        else None,
                    ),
                    dmc.Anchor(
                        dmc.Button(
                            children="Ver resultado",
                            disabled=not ultima_resposta_id,
                        ),
                        href=f"/app/assessment-vendedor/resultado/?usr={usr_atual.id}&resposta={ultima_resposta_id}"
                        if ultima_resposta_id
                        else None,
                    ),
                ]
            ),
            dmc.Card(
                bg="#e9e9e9",
                px="1rem",
                mt="5rem",
                children=dmc.Group(
                    spacing="xl",
                    children=[
                        DashIconify(
                            icon="fluent:play-48-filled",
                            color="#fff",
                            className="play-videos-av",
                        ),
                        html.Div(
                            style={"width": 350},
                            children=[
                                dcc.Markdown(
                                    "Acesse a nossa plataforma de vídeos **após realizar o teste do Assessment Boopt**"
                                ),
                                dmc.Anchor(
                                    href="",
                                    children=dmc.Button(
                                        children="Acessar",
                                        leftIcon=DashIconify(
                                            icon="fluent:filmstrip-play-16-filled",
                                            width=16,
                                        ),
                                        className="btn-borda-gradiente btn-acessar-videos",
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
