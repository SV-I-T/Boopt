from flask_login import LoginManager, UserMixin


class Usuario(UserMixin):
    pass


login_manager = LoginManager()


@login_manager.user_loader
def carregar_usuario(_id):
    return Usuario.get(_id)
