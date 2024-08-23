import dash_mantine_components as dmc
from flask_login import LoginManager

from utils.role import Role
from utils.usuario import Usuario

login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.login_message = "Faça o login para acessar esta página."


@login_manager.user_loader
def carregar_usuario(_id):
    usr = Usuario.consultar_pelo_id(_id)
    if not usr:
        return None
    return Usuario(**usr)


def layout_nao_autorizado():
    return [
        dmc.Title(children="Ops!", order=1),
        dmc.Title(
            children="Parece que você não tem autorização para acessar essa página",
            order=3,
            weight=500,
        ),
        dmc.Anchor(
            children="Clique aqui para voltar à página inicial",
            href="/",
            underline=True,
        ),
    ]


def checar_perfil(_func=None, *, permitir: tuple[Role] = None):
    def decorador(func: callable):
        def wrapper(*args, **kwargs):
            usr_atual = Usuario.atual()
            if usr_atual.is_authenticated and (
                permitir is None or usr_atual.role in permitir
            ):
                return func(*args, **kwargs)
            return layout_nao_autorizado()

        return wrapper

    if _func is None:
        return decorador
    else:
        return decorador(_func)
