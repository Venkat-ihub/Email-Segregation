# HR Email Parsing and Applicant Classification System

## 📄 Project Overview  
The HR Email Parsing and Applicant Classification System automates the recruitment process by parsing job application emails, extracting key applicant details (such as name, email, job role, and resume link), and storing this data in MongoDB. The system also includes a Django-based web interface for viewing and filtering applicants by job categories. Resumes are securely uploaded to Google Drive, generating shareable links.  

---

## ✨ Features  
- **Email Parsing**: Automatically fetches and processes new job application emails using IMAP.  
- **Job Role Extraction**: Identifies job roles from email content based on predefined keywords.  
- **Applicant Classification**: Categorizes applicants into groups like *IT-Based*, *Education-Based*, *Blue Collar*, and *Others*.  
- **Resume Management**: Uploads resumes to Google Drive and generates shareable links.  
- **Web Interface**: A Django-powered table to view and filter applicant data.  

---

## ⚙️ Setup Instructions  

### Prerequisites  
Ensure you have the following installed:  
- Python 3.8 or higher  
- MongoDB (local or remote)  
- Google Cloud Project for Google Drive API  
- Django 4.1 or higher  

### Clone the Repository  
```bash  
git clone https://github.com/Venkat-Balaji/Hr-App.git  
cd Hr-App
```
Install Dependencies
```bash
pip install -r requirements.txt  
```
## Configuration
### IMAP Credentials:
Create a cred.yml file in the management/commands folder with the following content:

```yaml
user: "your-email@example.com"  
password: "your-password"
```
### Google Drive API Setup:

In Google Cloud Console, create a Service Account and download the JSON key file.
Place the JSON key file in the project directory.
Update the SERVICE_ACCOUNT_FILE variable in listen_for_emails.py with the file's path.
Ensure SCOPES includes 'https://www.googleapis.com/auth/drive.file'.

### MongoDB Configuration:

Ensure MongoDB is running locally or remotely.
Update the MongoDB URI in listen_for_emails.py if needed.

## STEPS TO RUN THE PROGRAM:

- Install the dependencies.
- Open two command prompt windows in the project directory.
- Navigate to the application (my_app) in both the windows.
- Run "_python manage.py listen_for_emails_" to actively listen to the emails
- In another window run "_python manage.py runserver_" to locally host the application
- open  _**http://127.0.0.1:8000/applicants/**_ in the browser
