import dash_mantine_components as dmc
from dash import register_page
from flask_login import current_user, login_required
from utils.banco_dados import db
from utils.modelo_assessment import AssessmentVendedor
from utils.modelo_usuario import Usuario, checar_login

register_page(
    __name__,
    path="/app/assessment-vendedor",
    title="Assessment Vendedor",
    redirect_from=["/app/dashboard"],
)


@checar_login
def layout():
    usr_atual: Usuario = current_user

    aplicacao = AssessmentVendedor.buscar_ultimo(usr_atual.id_)
    resposta = aplicacao.get("resposta", None)

    return dmc.Stack(
        align="center",
        justify="center",
        px="1rem",
        children=[
            dmc.Text(
                "Bem-vindo ao Assessment de Vendedor",
                size=64,
                weight=600,
                align="center",
                mb="1rem",
            ),
            dmc.Text(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent ligula arcu, auctor vel tellus vitae, aliquam dignissim quam.",
                size=40,
                weight=500,
                align="center",
                mb="4rem",
            ),
            dmc.Anchor(
                dmc.Button(
                    children=dmc.Text(
                        "Começar o teste"
                        if aplicacao and not resposta
                        else "Sem teste disponível",
                        size=20,
                        weight=400,
                    ),
                    disabled=not (aplicacao and not resposta),
                    w=300,
                    h=50,
                    color="BooptLaranja",
                ),
                href=f"/app/assessment-vendedor/teste/?id={aplicacao['_id']}"
                if aplicacao and not resposta
                else None,
            ),
            dmc.Anchor(
                dmc.Button(
                    children=dmc.Text("Ver resultado", size=20, weight=400),
                    disabled=not resposta,
                    w=300,
                    h=50,
                ),
                href=f"/app/assessment-vendedor/resultado/?id={resposta}"
                if resposta
                else None,
            ),
        ],
    )
