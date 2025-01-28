# mongodb.py
from pymongo import MongoClient

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")
db = client["hr_app"]  # Replace "email_data" with your actual database name

applicants = db['applicants']