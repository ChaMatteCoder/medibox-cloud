from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repository = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        email = str(payload.email).lower()
        if self.repository.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = User(
            name=payload.name,
            email=email,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
        )
        return self.repository.create(user)

    def login(self, payload: UserLogin) -> Token:
        user = self.repository.get_by_email(str(payload.email).lower())
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=user.id, role=user.role)
        return Token(access_token=access_token)
