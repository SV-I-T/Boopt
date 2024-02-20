from os.path import join

from flask_mail import Mail

mail = Mail()


def template_email(body: str = "") -> str:
    with open(join("assets", "template_email.html"), encoding="utf-8") as f:
        template = f.read()
    return template.format(body=body)
