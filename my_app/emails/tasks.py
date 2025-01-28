# emails/tasks.py
from celery import shared_task
from imaplib import IMAP4_SSL
from email import message_from_bytes
from pymongo import MongoClient
from datetime import datetime
import yaml

@shared_task
def check_new_emails():
    # Load credentials from YAML
    with open("cred.yml") as f:
        content = f.read()
    my_credentials = yaml.load(content, Loader=yaml.FullLoader)
    user, password = my_credentials["user"], my_credentials["password"]

    # Connect to email server
    imap_url = 'imap.gmail.com'
    mail = IMAP4_SSL(imap_url)
    mail.login(user, password)
    mail.select('Inbox')

    # Search for unread emails
    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["email_data"]
    collection = db["applicants"]

    for num in mail_ids:
        status, msg_data = mail.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = message_from_bytes(response_part[1])

                # Extract details
                subject = msg['subject']
                sender = msg['from']
                body = ""
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode()

                # Parse subject for job role
                job_role = subject.split("Application for ")[-1] if "Application for" in subject else "Not specified"

                # Save email details to MongoDB
                document = {
                    "name": sender.split('<')[0].strip(),
                    "email": sender.split('<')[1].strip('>'),
                    "job_role": job_role,
                    "resume": "No resume attached",
                    "received_at": datetime.now(),
                    "subject": subject,
                    "body": body
                }
                collection.insert_one(document)

    mail.logout()
