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

    if aplicacao is not None:
        if "resposta" in aplicacao:
            BOTAO_TESTE = dmc.Button("Sem teste disponível", disabled=True)
            BOTAO_RESULTADO = dmc.Anchor(
                children=dmc.Button("Ver resultado"),
                href=f"/app/assessment-vendedor/resultado/?id={aplicacao['resposta']}",
            )
        else:
            BOTAO_TESTE = dmc.Anchor(
                href=f"/app/assessment-vendedor/teste/?id={aplicacao['_id']}",
                children=dmc.Button("Começar o teste"),
            )
            BOTAO_RESULTADO = dmc.Button("Ver resultado", disabled=True)
    else:
        BOTAO_TESTE = dmc.Button("Sem teste disponível", disabled=True)
        BOTAO_RESULTADO = dmc.Button("Ver resultado", disabled=True)

    return [
        dmc.Title("Bem-vindo ao Assessment de Vendedor", order=1, weight=700),
        BOTAO_TESTE,
        BOTAO_RESULTADO,
    ]
