from typing import Optional

from bson import ObjectId
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from pydantic import BaseModel, computed_field, field_validator
from utils.banco_dados import mongo
from werkzeug.security import check_password_hash, generate_password_hash


class Usuario(UserMixin, BaseModel):
    _id: Optional[ObjectId] = None
    nome: str
    sobrenome: str
    cpf: str
    email: Optional[str] = None
    senha: Optional[str] = None
    admin: bool = False
    sv: bool = False
    clientes: Optional[list[dict]] = []

    @computed_field
    @property
    def id(self) -> str:
        return str(self._id)

    def carregar_por_id(self, _id: str):
        usuario = mongo.cx["Boopt"]["Usuários"].find_one(
            {"_id": ObjectId(_id)}, {"senha_hash": 0, "_id": 0}
        )
        if not usuario:
            return None
        return Usuario(**usuario)

    def carregar_por_cpf(self, cpf):
        usuario = mongo.cx["Boopt"]["Usuários"].find_one(
            {"cpf": cpf}, {"senha_hash": 0, "_id": 0}
        )
        if not usuario:
            return None
        else:
            return Usuario(**usuario)

    def carregar_por_email(self, email):
        usuario = mongo.cx["Boopt"]["Usuários"].find_one(
            {"email": email}, {"senha_hash": 0, "_id": 0}
        )
        if not usuario:
            return None
        else:
            return Usuario(**usuario)

    def registrar_db(self) -> None:
        r = mongo.cx["Boopt"]["Usuários"].insert_one(self.model_dump())
        assert r, "Erro no registro de usuário."

    def entrar(self, cpf: str, senha: str, lembrar: bool = False) -> None:
        usuario = mongo.cx["Boopt"]["Usuários"].find_one({"cpf": cpf})
        assert usuario, "Usuário não existe"
        assert check_password_hash(usuario["senha_hash"], senha), "Senha incorreta"
        login_user(Usuario(**usuario), remember=lembrar)

    def sair(self) -> None:
        assert current_user.is_authenticated, "Não logado no momento"
        logout_user()


login_manager = LoginManager()
login_manager.login_view = "/login"


@login_manager.user_loader
def carregar_usuario(_id):
    return Usuario.carregar_por_id(_id)
