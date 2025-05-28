from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings
from fastapi import HTTPException, status , Depends
from fastapi.security import OAuth2PasswordBearer


outh2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    except Exception as e:
        return str(e)
    

def get_current_user(token: str = Depends(outh2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    