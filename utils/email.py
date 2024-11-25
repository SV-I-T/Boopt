from os.path import join

from flask_mail import Mail, Message

mail = Mail()


def attach_logo(msg: Message):
    msg.attach(
        "HORIZONTAL AZUL.png",
        "image/gif",
        open(join("static", "assets", "boopt", "horizontal_azul.svg"), "rb").read(),
        "inline",
        [["Content-ID", "<LogoBoopt>"]],
    )
