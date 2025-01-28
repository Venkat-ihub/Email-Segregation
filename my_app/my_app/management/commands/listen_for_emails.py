import imaplib
import email
from email.utils import parseaddr, parsedate_to_datetime
import yaml
from pymongo import MongoClient
from imapclient import IMAPClient
import time
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from django.core.management.base import BaseCommand

# Google Drive API setup
SERVICE_ACCOUNT_FILE = 'E:/Projs/iHub/hrapp/solar-century-441204-b4-ca56659a8d4b.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

# Load email credentials
with open("E:\Projs\iHub\hrapp\my_app\my_app\management\commands\cred.yml") as f:
    content = f.read()
my_credentials = yaml.load(content, Loader=yaml.FullLoader)
user, password = my_credentials["user"], my_credentials["password"]

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['hr_app']
collection = db['applicants']

# Job role classification based on keywords
JOB_CATEGORIES = {
    "IT BASED": ["developer", "engineer", "software", "data", "IT", "programmer", "analyst"],
    "EDUCATION BASED": ["teacher", "instructor", "professor", "educator", "trainer"],
    "BLUE COLLAR": ["mechanic", "technician", "driver", "electrician", "construction", "laborer"],
}

def connect_mail():
    client = IMAPClient('imap.gmail.com', ssl=True)
    client.login(user, password)
    client.select_folder('INBOX')
    return client

# Classify job role based on email body
IT_BASED_ROLES = [
    "Machine Learning Engineer", "Data Scientist", "Software Developer", "System Administrator",
    "Data Analyst", "Cybersecurity Analyst", "Web Developer", "Cloud Engineer"
]
EDUCATION_BASED_ROLES = [
    "Classroom Teacher", "School Administrator", "Guidance Counselor", "Librarian",
    "Special Education Teacher", "Instructional Designer", "Teacher Assistant",
    "Educational Consultant", "School Counselor", "Tutor"
]
BLUE_COLLAR_ROLES = [
    "Electrician", "Plumber", "Construction Laborer", "Welder", "Machinist",
    "HVAC Technician", "Bus Driver", "Auto Mechanic", "Factory Worker", "Forklift Operator"
]


def extract_applying_role(body):
    """Determine the job role based on keywords in the email body."""
    
    # Define keyword patterns for job roles
    it_role_patterns = {
        "Machine Learning Engineer": r"\b(ml\s?engineer|machine\s?learning\s?engineer)\b",
        "Data Scientist": r"\b(data\s?scientist)\b",
        "Software Developer": r"\b(software\s?developer)\b",
        "Software Engineer":r"\b(software\s?engineer)",
        "System Administrator": r"\b(system\s?administrator|sysadmin)\b",
        "Data Analyst": r"\b(data\s?analyst)\b",
        "Cybersecurity Analyst": r"\b(cybersecurity\s?analyst)\b",
        "Web Developer": r"\b(web\s?developer)\b",
        "Frontend Developer":r"\b(Frontend)\b",
        "Backend Developer":r"\b(backendtend)\b",
        "Cloud Engineer": r"\b(cloud\s?engineer|cloud\s?architect)\b",
    }

    education_role_patterns = {
        "Classroom Teacher": r"\b(classroom\s?teacher|teacher)\b",
        "School Administrator": r"\b(school\s?administrator)\b",
        "Guidance Counselor": r"\b(guidance\s?counselor)\b",
        "Librarian": r"\b(librarian)\b",
        "Special Education Teacher": r"\b(special\s?education\s?teacher|special\s?ed\s?teacher)\b",
        "Instructional Designer": r"\b(instructional\s?designer)\b",
    }

    blue_collar_patterns = {
        "Electrician": r"\b(electrician)\b",
        "Plumber": r"\b(plumber)\b",
        "Construction Laborer": r"\b(construction\s?laborer|construction\s?worker)\b",
        "Welder": r"\b(welder)\b",
        "Machinist": r"\b(machinist)\b",
        "HVAC Technician": r"\b(hvac\s?technician|hvac\s?tech)\b",
    }

    # Match IT roles
    for role, pattern in it_role_patterns.items():
        if re.search(pattern, body, re.IGNORECASE):
            return role, "IT BASED"
    
    # Match Education roles
    for role, pattern in education_role_patterns.items():
        if re.search(pattern, body, re.IGNORECASE):
            return role, "EDUCATION BASED"
    
    # Match Blue Collar roles
    for role, pattern in blue_collar_patterns.items():
        if re.search(pattern, body, re.IGNORECASE):
            return role, "BLUE COLLAR"
    
    # If no match, classify as "Others"
    return "Not specified", "OTHERS"



def classify_job_role(body):
    # Define keywords for different job categories
    it_keywords = ['software engineer', 'developer', 'programming', 'python', 'java', 'web developer', 'frontend', 'backend', 'IT']
    education_keywords = ['teacher', 'education', 'tutor', 'school', 'math', 'english', 'principal', 'professor', 'lecturer']
    blue_collar_keywords = ['electrician', 'plumber', 'construction', 'mechanic', 'driver', 'carpenter', 'welder', 'mason']
    
    # Convert body to lowercase for easier matching
    body = body.lower()

    # Search for keywords in the body and classify accordingly
    if any(keyword in body for keyword in it_keywords):
        applying_role = extract_applying_role(body)  # Get the applying role for IT jobs
        return "IT BASED", applying_role
    elif any(keyword in body for keyword in education_keywords):
        return "EDUCATION BASED", extract_applying_role(body)  # Use body to classify
    elif any(keyword in body for keyword in blue_collar_keywords):
        return "BLUE COLLAR", extract_applying_role(body)  # Use body to classify
    else:
        return "OTHERS", "Not Specified"

def process_email(raw_email,msg_id):
    # Parsing email content
    my_msg = email.message_from_bytes(raw_email)
    sender_name, sender_email = parseaddr(my_msg['from'])
    raw_date = my_msg['date']
    
    try:
        date_obj = parsedate_to_datetime(raw_date)
        date_received = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        date_received = "Unknown"
        print(f"Error parsing date: {e}")

    # Initialize body content and read it
    body = ""   
    for part in my_msg.walk():
        if part.get_content_type() == 'text/plain':
            payload = part.get_payload(decode=True)
            if payload:
                body += payload.decode(errors='ignore')

    
    # Extract job role and applying role from email body
    applying_role, job_role_category = extract_applying_role(body)

    # Add logic for processing attachments, resume, etc., as previously defined
    resume_link = "No resume attached"
    for part in my_msg.walk():
        if part.get_content_type() == 'text/plain':
            body += part.get_payload()
        elif part.get_content_type() == 'application/pdf':
            resume_filename = part.get_filename()
            
            # Upload the PDF file to Google Drive directly from memory
            if resume_filename:
                pdf_data = part.get_payload(decode=True)
                file_metadata = {
                    'name': resume_filename,
                    'parents': ['1JR4E2IlDZ2_dBLnFzbxnICvhCpcDPjNl']  # replace with your folder ID
                }
                media = MediaIoBaseUpload(io.BytesIO(pdf_data), mimetype='application/pdf')
                uploaded_file = drive_service.files().create(
                    body=file_metadata, media_body=media, fields='id'
                ).execute()
                
                # Generate a shareable link
                file_id = uploaded_file.get('id')
                drive_service.permissions().create(
                    fileId=file_id,
                    body={'type': 'anyone', 'role': 'reader'}
                ).execute()
                resume_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing" # Default, handle with Google Drive logic if attachment is found
    
    email_link = f"https://mail.google.com/mail/u/0/#inbox/{msg_id}" if msg_id else "No link available"

    # Prepare the data for MongoDB
    email_data = {
        "name": sender_name,
        "email": sender_email,
        "job_role": job_role_category,
        "applying_role": applying_role,
        "resume": resume_link,
        "date_received": date_received,
        "body": body,
        "email_link":email_link
    }

    # Insert into MongoDB
    try:
        result = collection.insert_one(email_data)
        print(f"Inserted document with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error inserting document: {e}")


def listen_for_emails():
    client = connect_mail()
    try:
        while True:
            client.idle()
            print("Waiting for new emails...")
            client.idle_check(timeout=60)
            client.idle_done()

            messages = client.search(['UNSEEN'])
            for msg_id in messages:
                raw_email = client.fetch([msg_id], ['RFC822'])[msg_id][b'RFC822']
                process_email(raw_email,msg_id)
    except Exception as e:
        print(f"Error in IMAP IDLE loop: {e}")
    finally:
        client.logout()

class Command(BaseCommand):
    help = 'Listen for new emails and store them in MongoDB'

    def handle(self, *args, **options):
        listen_for_emails()
