from pymongo import MongoClient
from utils.config import settings

# MongoDB connection
client = MongoClient(settings.MONGO_URI)
db = client["esg_database"]

# Single collection for all sections
esg_collection = db["ESGResponses"]

# Existing user collection for general user data
user_collection = db["user"]

# New collection for authentication (email and password)
auth_users_collection = db["authUsers"]

def get_collection():
    return esg_collection

def get_user_collection():
    return user_collection

def get_auth_users_collection():
    return auth_users_collection