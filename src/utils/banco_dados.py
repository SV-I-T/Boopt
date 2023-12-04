import os

from dotenv import load_dotenv
from flask_pymongo import PyMongo

load_dotenv()
mongo = PyMongo()
