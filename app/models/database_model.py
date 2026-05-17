from sqlalchemy import Column, Integer, String
from app.database.connection import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_name = Column(String, index=True)
    description = Column(String, nullable=True)
    target = Column(String)
    status = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String) 