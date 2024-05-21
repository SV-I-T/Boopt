from os.path import join

from flask_mail import Mail, Message

mail = Mail()


def attach_logo(msg: Message):
    msg.attach(
        "HORIZONTAL AZUL.png",
        "image/gif",
        open(join("assets", "imgs", "boopt", "horizontal_azul.svg"), "rb").read(),
        "inline",
        [["Content-ID", "<LogoBoopt>"]],
    )
