### This is for low level bare-bones, sessionless authentication
### If we want sessions where user can log in for extended time we would go the JWT route
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from backend.DB.database import dbSession
from backend.DB.models import User
from typing import Annotated
from pydantic import BaseModel
security = HTTPBasic()

import hashlib

def hash_pass(password):
    """hashes users input passwords using sha512"""
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

def get_current_user(db: dbSession, cred: HTTPBasicCredentials = Depends(security)) -> User:
    """
    Authenticates users with HTTP Basic Auth
    :param db: Database Session
    :param cred: Username/password from Auth header
    :return: Authenticated User obj
    """
    user = db.query(User).filter(User.username == cred.username).first()

    if not user or user.password_hash != hash_pass(cred.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return user

def login_user(db: dbSession, cred: HTTPBasicCredentials) -> User:
    user = db.query(User).filter(User.username == cred.username).first()
    if not user or user.password_hash != hash_pass(cred.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return user

def create_user(username: str, password: str, db: dbSession) -> User:
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = hash_pass(password)

    user = User(username=username, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class PassChange(BaseModel):
    password: str

class UsernameChange(BaseModel):
    username: str


def change_pass(db: dbSession, cred: HTTPBasicCredentials, new_pass: PassChange) -> User:
    """

    :param db: Database connection
    :param cred: Current username/password from Auth header
    :param new_pass: new password from request body
    :return: User obj
    """
    user = db.query(User).filter(User.username == cred.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password_hash != hash_pass(cred.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    user.password_hash = hash_pass(new_pass.password)
    db.commit()
    db.refresh(user)
    return user

def change_username(db: dbSession, cred: HTTPBasicCredentials, new_name: UsernameChange) -> User:
    user = db.query(User).filter(User.username == cred.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password_hash != hash_pass(cred.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if db.query(User).filter(User.username == new_name.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user.username = new_name.username
    db.commit()
    db.refresh(user)
    return user

#CurrentUser and Credentials for future dependency injections (Makes code cleaner/less verbose)
CurrentUser = Annotated[User, Depends(get_current_user)]
HTTPcred = Annotated[HTTPBasicCredentials, Depends(security)]


class RegisterRequest(BaseModel):
    username: str
    password: str


