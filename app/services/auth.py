from sqlmodel import Session, select

from app.models.entities import User


def register_user(session: Session, username: str, password: str, role: str = "analista") -> User:
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        return existing
    user = User(username=username, password=password, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, username: str, password: str) -> User | None:
    return session.exec(
        select(User).where(User.username == username).where(User.password == password)
    ).first()
