from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import database_model


class Login(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    def validate_either(self):
        if not (self.username or self.email):
            raise ValueError("Either username or email must be provided")


# JWT / auth settings
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_ctx.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(database_model.User).filter(database_model.User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise credentials_exception

    user = db.query(database_model.User).filter(database_model.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
