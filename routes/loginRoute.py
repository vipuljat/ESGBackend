from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from passlib.hash import bcrypt
import logging
from utils.jwt_handler import create_access_token
from database import get_auth_users_collection

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

# Get the auth_users collection
auth_users_collection = get_auth_users_collection()

# Request model for login
class LoginRequest(BaseModel):
    email: str
    password: str

# Response model for token, including user_id
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

@router.post("/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest):
    try:
        if auth_users_collection is None:
            logger.error("Database collection 'auth_users' is None")
            raise HTTPException(status_code=500, detail="Database configuration error: collection is None")
        user = auth_users_collection.find_one({"email": login_data.email})
        if not user:
            logger.warning(f"Login failed: Invalid email: {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid email")
        if "_id" not in user:
            logger.error(f"User with email {login_data.email} has missing _id field")
            raise HTTPException(status_code=500, detail="User account is corrupted: missing _id")
        user["_id"] = str(user["_id"])
        password_hash = user.get("password")
        if not password_hash or not isinstance(password_hash, str) or not password_hash.startswith('$2b$'):
            logger.error(f"User with email {login_data.email} has invalid or missing password field: {password_hash}")
            raise HTTPException(status_code=500, detail="User account is corrupted: invalid password format")
        try:
            if not bcrypt.verify(login_data.password, password_hash):
                logger.warning(f"Login failed: Invalid password for email: {login_data.email}")
                raise HTTPException(status_code=401, detail="Invalid password")
        except ValueError as ve:
            logger.error(f"Password verification failed for email {login_data.email}: {str(ve)}")
            raise HTTPException(status_code=500, detail="Password verification error")
        
        access_token = create_access_token(data={"sub": user["email"]})
        logger.info(f"Generating token for email: {user['email']}")
        logger.info(f"User logged in successfully: {user['_id']}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["_id"]
        }
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")