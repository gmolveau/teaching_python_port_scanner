from models import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///simple.db")

with Session(engine) as session:
    # Insert
    session.add_all([User(name="Alice"), User(name="Bob")])
    session.commit()

    # Query all
    users = session.scalars(select(User)).all()
    for user in users:
        print(user.id)

    # Query one by name
    alice = session.scalar(select(User).where(User.name == "Alice"))
    print(alice)
