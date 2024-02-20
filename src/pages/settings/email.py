from os.path import join
from time import sleep

import dash_mantine_components as dmc
from dash import (
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    html,
    no_update,
    register_page,
)
from dash.exceptions import PreventUpdate
from flask_mail import Message
from utils.email import mail, template_email

register_page(__name__, path="/configuracoes/email", title="Teste de email")


def layout():
    return html.Div(
        style={"width": 600},
        children=[
            dmc.TextInput(type="email", label="Destinatário", id="email-destinatario"),
            dmc.TextInput(label="Assunto", id="email-assunto"),
            dmc.Textarea(label="Corpo", id="email-corpo"),
            dmc.Button(
                "Enviar",
                id="email-btn-enviar",
                loaderPosition="right",
                loaderProps=dict(variant="dots"),
            ),
            html.Div(id="feedback-email"),
        ],
    )


clientside_callback(
    ClientsideFunction("clientside", "ativar"),
    Output("email-btn-enviar", "loading"),
    Input("email-btn-enviar", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("feedback-email", "children"),
    Output("notificacoes", "children", allow_duplicate=True),
    Output("email-btn-enviar", "loading", allow_duplicate=True),
    Input("email-btn-enviar", "n_clicks"),
    State("email-destinatario", "value"),
    State("email-assunto", "value"),
    State("email-corpo", "value"),
    prevent_initial_call=True,
)
def enviar_email(n: int, destinatario: str, assunto: str, corpo: str):
    if not n:
        raise PreventUpdate
    elif not destinatario or not assunto or not corpo:
        ALERTA = dmc.Alert("Preencha todos os campos", title="Atenção")
        NOTIFICACAO = no_update
    else:
        # sleep(5)
        msg = Message(
            subject=assunto,
            recipients=[destinatario],
            html=template_email(body=corpo),
        )
        msg.attach(
            "HORIZONTAL AZUL.png",
            "image/gif",
            open(join("assets", "imgs", "boopt", "HORIZONTAL AZUL.png"), "rb").read(),
            "inline",
            [["Content-ID", "<LogoBoopt>"]],
        )
        mail.send(msg)
        ALERTA = no_update
        NOTIFICACAO = dmc.Notification(
            id="notificacao-email-enviado",
            action="show",
            title="Pronto!",
            message="O email foi enviado com sucesso.",
        )
    LOADING = False
    return ALERTA, NOTIFICACAO, LOADING
