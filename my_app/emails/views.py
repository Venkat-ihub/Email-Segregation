from django.shortcuts import render
from my_app.mongodb import applicants  # Import the MongoDB collection from your config file
from datetime import datetime
from pymongo import MongoClient
import re

client = MongoClient("mongodb://localhost:27017/")
db = client['hr_app']
collection = db['applicants']

def home(request):
    return render(request, 'emails/home.html')

def job_application_emails(request):
    # Filter job application emails
    job_emails = collection.find({"job_role": {"$ne": "Not specified"}})
    return render(request, 'emails/job_application_emails.html', {'emails': job_emails})

def other_emails(request):
    # Filter other emails
    other_emails = collection.find({"job_role": "Not specified"})
    return render(request, 'emails/other_emails.html', {'emails': other_emails})


CATEGORIES = ["ALL", "IT BASED", "EDUCATION BASED", "BLUE COLLAR", "OTHERS"]
def filter_applicants_by_category(applicants, category):
    # If 'ALL', return all applicants
    if category == 'ALL':
        return applicants

    # Otherwise, filter based on keywords in the job_role or body fields
    keywords = CATEGORIES.get(category, [])
    filtered_applicants = [
        applicant for applicant in applicants
        if any(keyword.lower() in (applicant.get('job_role', '') + applicant.get('body', '')).lower() for keyword in keywords)
    ]
    return filtered_applicants

def extract_applying_role(body):
    """Determine the job role based on keywords in the email body."""
    
    # Define keyword patterns for job roles (adjust as per your list of roles)
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
        "Backend Developer":r"\b(backend)\b",
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

def applicant_list(request):
    # Get the category filter from the request URL, default to 'ALL' if not set
    category = request.GET.get('category', 'ALL')
    
    # Get the date filter from the request URL (format: YYYY-MM-DD), default to None if not set
    selected_date = request.GET.get('date')

    # Fetch all applicants from MongoDB and sort by 'date_received' in descending order
    applicant_docs = applicants.find().sort('date_received', -1)
    search_query = request.GET.get('search', '')
    # Filter the applicants based on the category and date
    filtered_applicants = []
    for applicant in applicant_docs:
        # If there's no 'body' field, set it to empty
        body = applicant.get('body', "")
        
        # Extract the applying role and category
        job_role, applicant_category = extract_applying_role(body)
        
        # Get the 'date_received' field and convert it to a date object
        date_received = applicant.get('date_received')
        if isinstance(date_received, str):
            date_received = datetime.strptime(date_received, '%Y-%m-%d %H:%M:%S')

        # Filter based on category and date
        if (
            (category == 'ALL' or category == applicant_category) and
            (selected_date is None or date_received.date() == datetime.strptime(selected_date, '%Y-%m-%d').date()) and 
            (search_query.lower() in applicant.get('name', '').lower() or
             search_query.lower() in applicant.get('email', '').lower() or
             search_query.lower() in job_role.lower() or
             search_query.lower() in body.lower())
        ):
            filtered_applicants.append({
                'name': applicant['name'],
                'email': applicant['email'],
                'job_role': job_role,  # Only the job role (e.g., 'Machine Learning Engineer')
                'resume': applicant['resume'],
                'email_link': applicant.get('email_link', ''),
                'date_received': date_received.strftime("%d-%m-%Y | %I:%M:%S %p"),  # 12-hour format with AM/PM
            })

    return render(request, 'emails/applicant_list.html', {
        'applicants': filtered_applicants,
        'category': category,
        'selected_date': selected_date,
        'search_query': search_query,
    })
