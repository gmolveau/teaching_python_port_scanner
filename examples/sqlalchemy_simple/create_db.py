# /// script
# dependencies = ["sqlalchemy"]
# ///
#
# Run with: uv run create_db.py

from models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite:///simple.db")
Base.metadata.create_all(engine)
