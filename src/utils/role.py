from enum import Enum


class Role(str, Enum):
    DEV = "Desenvolvedor"
    CONS = "Consultor"
    ADM = "Administrador"
    GEST = "Gestor"
    USR = "Usuário"
    CAND = "Candidato"
