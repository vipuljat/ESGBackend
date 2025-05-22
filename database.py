from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://Vipul:ESG@cluster0.et73cxg.mongodb.net/")
db = client["esg_database"]

# Single collection for all sections
esg_collection = db["ESGResponses"]

def get_collection():
    return esg_collection