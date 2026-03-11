# /// script
# dependencies = ["sqlalchemy"]
# ///
#
# Run with: uv run examples/sqlalchemy_blog/main.py

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Base, BlogPost, Like, User

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as session:
    # --- Create users ---
    alice = User(username="alice")
    bob = User(username="bob")
    session.add_all([alice, bob])
    session.commit()

    # --- Alice writes a post ---
    post = BlogPost(
        title="Hello SQLAlchemy",
        content="SQLAlchemy v2 uses mapped_column and Mapped for type-safe models.",
        author=alice,
    )
    session.add(post)
    session.commit()

    # --- Bob likes Alice's post ---
    like = Like(user=bob, post=post)
    session.add(like)
    session.commit()

    # --- Prevent duplicate likes (UniqueConstraint) ---
    try:
        duplicate = Like(user=bob, post=post)
        session.add(duplicate)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Bob already liked this post — duplicate prevented.")

    # --- Query: posts with their like count ---
    # select() is the SQLAlchemy v2 way to build queries
    stmt = select(BlogPost)
    for p in session.scalars(stmt):
        print(f"'{p.title}' by {p.author.username} — {len(p.likes)} like(s)")

    # --- Query: posts liked by bob (via secondary relationship) ---
    print(f"\nPosts liked by {bob.username}:")
    for p in bob.liked_posts:
        print(f"  - '{p.title}'")
