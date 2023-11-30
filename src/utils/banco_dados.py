import os

from flask_pymongo import PyMongo

mongo = PyMongo(uri=os.environ.get("MONGO_URI"))
