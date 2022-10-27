from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os

load_dotenv('.env')

USER = os.getenv("MEGADADOS_USER")
PASSWORD = os.getenv("MEGADADOS_PASSWORD")
SERVER = os.getenv("MEGADADOS_SERVER")
DB = os.getenv("MEGADADOS_DB")

SQLALCHEMY_DATABASE_URL = f"mysql://{USER}:{PASSWORD}@{SERVER}/{DB}"

if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
