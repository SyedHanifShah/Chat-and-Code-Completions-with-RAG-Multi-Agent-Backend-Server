from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel
from typing import Optional, Annotated, Dict
from utils import get_secret_key, DEFAULT_SYSTEM_PROMPT, RequestBody
import models
from completion import completion_model, code_model
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from langchain_core.messages import AIMessage






SECRET_KEY = get_secret_key()
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    id: int
    username: str
    email: str
    organization: str
    role : str
    full_name:str
    password: str
    disabled: bool


   
class UserInDB(UserBase):
    password: str






oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app =  FastAPI()
models.Base.metadata.create_all(bind= engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session, Depends(get_db)]




def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')  # Convert plaintext password to bytes
    hashed_password_bytes = hashed_password.encode('utf-8')  # Convert hashed password to bytes
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password



def get_user(db, username: str) -> Dict[str, str]:
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        # Convert the user model instance to a dictionary
        user_data = user.__dict__
        return UserInDB(**user_data)
    

def check_user_email(db, email:str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        return False
    return True

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta:  Optional[timedelta]= None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(db: Session = Depends(get_db),token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(db: Session = Depends(get_db) ,current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


@app.post("/createuser", response_model=Token)
async def create_user(user: UserBase, db:db_dependency):
    is_email_already_registered = check_user_email( db, user.email)
    if not is_email_already_registered:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Email already exists.")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(id=user.id, username=user.username, email=user.email, organization=user.organization,
                   role=user.role, full_name=user.full_name, password=hashed_password , disabled = False)
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=UserBase)
async def read_users_me(db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items")
async def read_own_items(db:db_dependency , current_user: UserBase = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]






# completions model  endpoint 
@app.post('/completions/{type}')
async def triger_completions(type:str , request_body: RequestBody ,db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    res = None
    if type == "chat":
        res = completion_model(request_body=request_body)
    elif type == "code":
        result = code_model(request_body= request_body)
        res = AIMessage(content= result)
    return res



@app.post('/rag/upload')
async def reg_model(query:str, db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_active_user)):
    user = current_user
    print(user)
    return AIMessage(content=user,)




