from sqlalchemy import Boolean, Column, Integer , String
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)        
    full_name = Column(String(70))                    
    email = Column(String(100), unique=True)         
    organization = Column(String(100))               
    role = Column(String(50))                        
    password = Column(String(255))                  
    disabled = Column(Boolean)