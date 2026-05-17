from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
import passlib.context as passlib_context


from app.database import connection
from app.database.connection import get_db
from app.models import database_model
from app.schemas import pydantic_schema
from app.auth import authentication
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

database_model.Base.metadata.create_all(bind=connection.engine)

pwd_ctx = passlib_context.CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/", response_model=List[pydantic_schema.Scan])
def read_all_scans(db: Session = Depends(get_db), current_user: database_model.User = Depends(authentication.get_current_user)):
    scans = db.query(database_model.Scan).all()
    return scans

@app.get("/scans/{scan_id}", response_model=pydantic_schema.Scan)
def read_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(database_model.Scan).filter(database_model.Scan.id == scan_id).first()
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@app.post("/scans/", response_model=pydantic_schema.Scan)
def create_scan(scan: pydantic_schema.ScanCreate, db: Session = Depends(get_db)):
    db_scan = database_model.Scan(**scan.dict())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

@app.put("/scans/{scan_id}", response_model=pydantic_schema.Scan)
def update_scan(scan_id: int, scan: pydantic_schema.ScanCreate, db: Session = Depends(get_db)):
    db_scan = db.query(database_model.Scan).filter(database_model.Scan.id == scan_id).first()
    if db_scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    for key, value in scan.dict().items():
        setattr(db_scan, key, value)
    db.commit()
    db.refresh(db_scan)
    return db_scan

@app.delete("/scans/{scan_id}", response_model=pydantic_schema.Scan)
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    db_scan = db.query(database_model.Scan).filter(database_model.Scan.id == scan_id).first()
    if db_scan is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    db.delete(db_scan)
    db.commit()
    return db_scan

@app.post("/users/", response_model=pydantic_schema.UserOut, status_code=201)
def create_user(user: pydantic_schema.UserCreate, db: Session = Depends(get_db)):
    # check if username or email already exists
    existing = (
        db.query(database_model.User)
        .filter(or_(database_model.User.username == user.username, database_model.User.email == user.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="username or email already exists")

    # hash password and create user
    hashed_password = pwd_ctx.hash(user.password)
    db_user = database_model.User(username=user.username, email=user.email, password=hashed_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username or email already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"database error: {e}")

    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}


@app.post('/token', include_in_schema=False)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authentication.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')

    access_token = authentication.create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}