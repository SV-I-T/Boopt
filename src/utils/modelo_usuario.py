import re
from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

import dash_mantine_components as dmc
import openpyxl
from bson import ObjectId
from flask_login import LoginManager, UserMixin, current_user
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


class Role(str, Enum):
    DEV = "Desenvolvedor"
    CONS = "Consultor"
    ADM = "Administrador"
    GEST = "Gestor"
    USR = "Usuário"
    CAND = "Candidato"


class Usuario(BaseModel, UserMixin):
    id_: ObjectId = Field(alias="_id")
    nome: Optional[str] = None
    data: Optional[datetime] = None
    cpf: Optional[str] = None
    email: Optional[str] = None
    role: Optional[Role] = Role.CAND
    empresa: Optional[ObjectId] = None
    clientes: Optional[list[ObjectId]] = None
    cargo: Optional[str] = None
    unidades: Optional[list[str]] = None

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @computed_field
    @property
    def id(self) -> str:
        return str(self.id_)

    @computed_field
    @property
    def primeiro_nome(self) -> str:
        if len(parts := self.nome.split(" ")) >= 2:
            return " ".join(parts[:2])
        return " ".join(parts)

    @classmethod
    def buscar(
        cls, identificador: Literal["_id", "email", "cpf"], valor: str | ObjectId
    ):
        if identificador == "_id" and not isinstance(valor, ObjectId):
            valor = ObjectId(valor)
        usr = db("Boopt", "Usuários").find_one({identificador: valor})
        assert usr, "Este usuário não foi encontrado."

        return cls(**usr)

    @classmethod
    @cache_simple.memoize(timeout=600)
    def buscar_login(cls, _id: str) -> dict | None:
        if _id == "None":
            return None
        usr = db("Boopt", "Usuários").find_one(
            {"_id": ObjectId(_id)},
        )
        print(f"Carregando usuário {usr['nome']}")
        return usr

    def validar_senha(self, senha: str) -> None:
        assert check_password_hash(
            self.senha_hash, senha
        ), "A senha digitada está incorreta."

    def atualizar(self, novos_dados: dict) -> None:
        r = db("Boopt", "Usuários").update_one(
            {"_id": self.id_},
            {"$set": {campo: valor for campo, valor in novos_dados.items()}},
        )

        assert r.acknowledged, "Ocorreu algum problema. Tente novamente mais tarde."

    def buscar_empresas(self) -> Cursor | list:
        if self.role == Role.DEV:
            query = {}
        elif self.role == Role.CONS:
            query = {"_id": {"$in": self.clientes}}
        elif self.role == Role.ADM:
            query = {"_id": self.empresa}
        elif self.role == Role.GEST:
            query = {"_id": self.empresa, "unidade": {"$in": self.unidades}}

        else:
            return []

        return db("Boopt", "Empresas").find(
            query, projection={"_id": 1, "nome": 1}, sort={"nome": 1}
        )


class NovoUsuario(BaseModel):
    nome: str
    cpf: str
    email: Optional[str] = None
    data: datetime
    cargo: str
    empresa: ObjectId
    role: Role
    clientes: Optional[list[ObjectId]] = None
    unidades: Optional[list[str]] = None

    class Config:
        arbitrary_types_allowed = True
        str_strip_whitespace = True

    @field_validator("nome", "cpf", "data", "empresa", "cargo", mode="before")
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


class NovosUsuariosBatelada(BaseModel):
    usuarios: list[NovoUsuario] = Field(default_factory=list)

    def registrar_usuarios(self) -> None:
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
    def carregar_planilha(cls, planilha, empresa: ObjectId, role: Role):
        wb = openpyxl.load_workbook(planilha)
        assert (
            "Cadastro" in wb.sheetnames
        ), "A planilha 'Cadastro' não foi encontrada. Certifique-se que o arquivo segue o modelo fornecido."
        ws = wb["Cadastro"]
        linhas = [[cell.value for cell in row] for row in ws.rows]
        assert (
            [
                "Primeiro Nome",
                "Sobrenome",
                "CPF",
                "Data de Nascimento",
                "Email",
                "Cargo/Função",
            ]
            == linhas[0]
        ), "O arquivo não está no modelo esperado. Certifique-se de não modificar o cabeçalho do modelo fornecido."

        assert (
            len(linhas) > 1
        ), "Parece que o arquivo está vazio. Preencha-o e tente enviar novamente."

        usuarios = [
            {
                "nome": linha[0],
                "sobrenome": linha[1],
                "cpf": linha[2],
                "data": linha[3].strftime("%Y-%m-%d") if linha[3] else None,
                "email": linha[4] if linha[4] is not None else "",
                "cargo": linha[5],
                "empresa": empresa,
                "role": Role,
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


def checar_perfil(_func=None, *, permitir: tuple[Role] = None):
    def decorador(func: callable):
        def wrapper(*args, **kwargs):
            usr_atual: Usuario = current_user
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
