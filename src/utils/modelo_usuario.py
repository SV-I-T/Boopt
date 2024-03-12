import re
from typing import Any, Literal, Optional, Union

import dash_mantine_components as dmc
import openpyxl
from bson import ObjectId
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from pydantic import BaseModel, Field, ValidationInfo, computed_field, field_validator
from pymongo.cursor import Cursor
from utils.banco_dados import db
from utils.cache import cache_simple
from werkzeug.security import check_password_hash, generate_password_hash

CARGOS_PADROES = sorted(
    [
        "Vendedor",
        "Diretor Comercial",
        "Gerente de Loja",
        "Atendente",
        "Supervisor de Loja",
        "Regional",
    ]
)


class NovoUsuario(BaseModel):
    nome: str
    sobrenome: str
    cpf: str
    email: Optional[str] = None
    data: str
    cargo: str
    empresa: Union[None, str, ObjectId]
    admin: bool = False
    gestor: bool = False
    recruta: bool = False

    class Config:
        arbitrary_types_allowed = True
        str_strip_whitespace = True

    @field_validator("empresa", mode="before")
    @classmethod
    def validar_empresa(cls, v: Any) -> ObjectId | None:
        assert bool(v), "O campo 'Empresa' é obrigatório"
        if not v:
            return None
        elif isinstance(v, str):
            return ObjectId(v)
        else:
            return None

    @field_validator(
        "nome", "sobrenome", "cpf", "data", "empresa", "cargo", mode="before"
    )
    @classmethod
    def em_branco(cls, v: Any, info: ValidationInfo) -> Any:
        assert bool(v), f"O campo '{info.field_name.capitalize()}' é obrigatório."
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, email: str) -> str | None:
        if not email:
            return None
        assert re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ).fullmatch(email), f"O e-mail '{email}' é inválido."
        return email

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, cpf: str) -> str:
        cpf = cpf.replace(".", "").replace("-", "")
        assert len(cpf) == 11 and cpf.isdigit(), f"O CPF {cpf} é inválido."
        cpf_d = tuple(map(int, cpf))
        resto1 = sum(((10 - i) * n for i, n in enumerate(cpf_d[:9]))) % 11
        regra1 = (resto1 <= 1 and cpf_d[-2] == 0) or (
            resto1 >= 2 and cpf_d[-2] == 11 - resto1
        )
        resto2 = sum(((11 - i) * n for i, n in enumerate(cpf_d[:10]))) % 11
        regra2 = (resto2 <= 1 and cpf_d[-1] == 0) or (
            resto2 >= 2 and cpf_d[-1] == 11 - resto2
        )
        assert regra1 and regra2, f"O CPF {cpf} é inválido."
        assert not db("Boopt", "Usuários").count_documents(
            {"cpf": cpf}
        ), f"O CPF '{cpf}' já foi cadastrado."
        return cpf

    @computed_field
    @property
    def senha_hash(self) -> str:
        return generate_password_hash("".join(self.data.split("-")[::-1]))

    def registrar(self) -> None:
        r = db("Boopt", "Usuários").insert_one(self.model_dump())
        assert (
            r.acknowledged
        ), "Não conseguimos criar o usuário. Tente novamente mais tarde."


class Usuario(BaseModel, UserMixin):
    id_: ObjectId = Field(alias="_id")
    nome: str
    sobrenome: str
    data: str
    senha_hash: str
    cpf: str
    email: str
    cargo: str
    empresa: ObjectId
    admin: bool = False
    gestor: bool = False
    recruta: bool = False

    class Config:
        arbitrary_types_allowed = True

    @computed_field
    @property
    def id(self) -> str:
        return str(self.id_)

    def logar(self, lembrar: bool = False) -> None:
        login_user(self, remember=lembrar, force=True)

    @classmethod
    def buscar(cls, identificador: Literal["_id", "email", "cpf"], valor: str):
        if identificador == "_id":
            valor = ObjectId(valor)
        usr = db("Boopt", "Usuários").find_one({identificador: valor})
        assert usr, "Este usuário não foi encontrado."

        return cls(**usr)

    def validar_senha(self, senha: str) -> None:
        assert check_password_hash(
            self.senha_hash, senha
        ), "A senha digitada está incorreta."

    def atualizar(self, novos_dados: dict[str, str]) -> None:
        r = db("Boopt", "Usuários").update_one(
            {"_id": self.id_},
            {"$set": {campo: valor for campo, valor in novos_dados.items()}},
        )

        assert r.acknowledged, "Ocorreu algum problema. Tente novamente mais tarde."

    def alterar_senha(
        self, senha_atual: str, senha_nova: str, senha_nova_check: str
    ) -> bool:
        senha_hash = db("Boopt", "Usuários").find_one(
            {"_id": self.id_}, {"_id": 0, "senha_hash": 1}
        )["senha_hash"]
        assert check_password_hash(
            senha_hash, senha_atual
        ), "A senha atual não está correta."

        assert not check_password_hash(
            senha_hash, senha_nova
        ), "A senha nova não pode ser igual à senha atual."

        assert senha_nova == senha_nova_check, "As senhas novas não combinam."

        r = db("Boopt", "Usuários").update_one(
            {"_id": self.id_},
            {"$set": {"senha_hash": generate_password_hash(senha_nova)}},
        )
        assert r.acknowledged, "Ocorreu algum problema. Tente novamente mais tarde."
        return True

    def buscar_empresas(self) -> Cursor | None:
        if self.admin:
            return db("Boopt", "Empresas").find(
                projection={"_id": 1, "nome": 1}, sort={"nome": 1}
            )
        elif self.gestor:
            return db("Boopt", "Empresas").find(
                {"_id": self.empresa},
                projection={"_id": 1, "nome": 1},
                sort={"nome": 1},
            )
        else:
            return None

    @classmethod
    @cache_simple.memoize(timeout=600)
    def buscar_login(cls, _id: str) -> dict | None:
        print("Carregando usuário")
        if _id == "None":
            return None
        return db("Boopt", "Usuários").find_one(
            {"_id": ObjectId(_id)},
        )

    def sair(self) -> None:
        logout_user()
        cache_simple.delete_memoized(Usuario.buscar_login, Usuario)


class NovosUsuariosBatelada(BaseModel):
    usuarios: list[NovoUsuario] = Field(default_factory=list)

    def registrar_usuarios(self, empresa: ObjectId) -> None:
        for i in range(len(self.usuarios)):
            self.usuarios[i].empresa = empresa

        r = db("Boopt", "Usuários").insert_many(
            [usuario.model_dump() for usuario in self.usuarios]
        )
        assert (
            r.acknowledged
        ), "Não conseguimos criar os usuários. Tente novamente mais tarde."

    @classmethod
    def gerar_modelo(cls, cargos_padres=list[str]) -> openpyxl.Workbook:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Cadastro"
        ws.append(
            [
                "Primeiro Nome",
                "Sobrenome",
                "CPF",
                "Data de Nascimento",
                "Email",
                "Cargo/Função",
            ]
        )
        ws.column_dimensions["C"].number_format = "@"
        ws.column_dimensions["D"].number_format = "DD/MM/YYYY"
        for col in ("A", "B", "E"):
            ws.column_dimensions[col].width = 32
        for col in ("C", "D", "F"):
            ws.column_dimensions[col].width = 16

        tabela = Table(
            displayName="Usuarios",
            ref="A1:F2",
            tableStyleInfo=TableStyleInfo(
                name="TableStyleMedium2",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
            ),
        )

        val_cargos = DataValidation(
            type="list",
            formula1=f'"{",".join(cargos_padres)}"',
            allow_blank=True,
            showErrorMessage=False,
        )

        ws.add_table(tabela)
        ws.add_data_validation(val_cargos)
        val_cargos.add("F2")

        return wb

    @classmethod
    def carregar_planilha(cls, planilha):
        wb = openpyxl.load_workbook(planilha)
        assert "Cadastro" in wb.sheetnames, "A planilha 'Cadastro' não foi encontrada."
        ws = wb["Cadastro"]
        linhas = [[cell.value for cell in row] for row in ws.rows]
        assert [
            "Primeiro Nome",
            "Sobrenome",
            "CPF",
            "Data de Nascimento",
            "Email",
            "Cargo/Função",
        ] == linhas[0], "O cabeçalho da tabela não segue o modelo fornecido."

        usuarios = [
            {
                "nome": linha[0],
                "sobrenome": linha[1],
                "cpf": linha[2],
                "data": linha[3].strftime("%Y-%m-%d"),
                "email": linha[4],
                "cargo": linha[5],
            }
            for linha in linhas[1:]
        ]

        return cls(usuarios=usuarios)


login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.login_message = "Faça o login para acessar esta página."


@login_manager.user_loader
def carregar_usuario(_id):
    usr = Usuario.buscar_login(_id)
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


def checar_login(_func=None, *, admin: bool = False, gestor: bool = False):
    """
    A decorator function that checks if the user is authenticated and has the necessary role permissions before allowing access to the decorated function.
    It takes in either a function or keyword arguments for admin and gestor roles, and returns a wrapper function that enforces the authentication and role permissions.
    """

    def decorador(func: callable):
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated:
                if (
                    (not admin and not gestor)
                    or (admin and current_user.admin)
                    or (gestor and current_user.gestor)
                ):
                    return func(*args, **kwargs)

            return layout_nao_autorizado()

        return wrapper

    if _func is None:
        return decorador
    else:
        return decorador(_func)
