from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo.collection import Collection

load_dotenv()
mongo = PyMongo()


def db(colecao: str, tabela: str) -> Collection:
    return mongo.cx[colecao][tabela]
