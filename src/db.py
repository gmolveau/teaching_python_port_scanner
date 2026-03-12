import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite")

engine = create_engine(DATABASE_URL)


def get_session() -> Session:
    return Session(engine)
