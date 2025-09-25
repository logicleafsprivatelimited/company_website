import os
import smtplib
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.oauth2.credentials
import google.auth
from google.cloud import firestore
import datetime

# --- Initialization ---
# Load environment variables from a .env file for security
load_dotenv() 

# Initialize the FastAPI application
app = FastAPI()

# --- CORS Middleware ---
# This is crucial! It allows your HTML frontend (running on a different address) 
# to make requests to this Python backend.
# For production, you should restrict origins to your actual website domain.
origins = ["*"]  # For development, we allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Initialization ---
try:
    # Initialize the Firestore Client using your credentials file
    db = firestore.Client.from_service_account_json("firebase-credentials.json")
except FileNotFoundError:
    print("FATAL ERROR: firebase-credentials.json not found. The server cannot connect to the database.")
    # In a real app, you might want to exit here, but for now we'll let it run and fail on request.
    db = None
except Exception as e:
    print(f"FATAL ERROR: An unexpected error occurred during Firebase initialization: {e}")
    db = None


# --- Email Credentials ---
# Load your secure credentials from the .env file
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# --- API Endpoint to Handle Form Submissions ---
@app.post("/submit-form")
async def handle_form_submission(
    Name: str = Form(...),
    Email: str = Form(...),
    Phone: str = Form(...),
    Subject: str = Form(...),
    Message: str = Form(...)
):
    """
    This single endpoint receives data from both contact forms.
    It saves the submission to Firestore and sends an email.
    """
    # Server-side validation to ensure email credentials are set up
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("ERROR: Server email configuration is incomplete. Check the .env file.")
        raise HTTPException(
            status_code=500,
            detail="The server is not configured to send emails."
        )

    if not db:
        print("ERROR: Firestore client is not available.")
        raise HTTPException(status_code=500, detail="Database connection is not configured.")

    try:
        # --- Action 1: Save the submission data to Firestore ---
        form_data = {
            "name": Name,
            "email": Email,
            "phone": Phone,
            "subject": Subject,
            "message": Message,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        # Create a new document in the 'submissions' collection
        db.collection("submissions").add(form_data)

        # --- Action 2: Send the notification email ---
        email_subject = f"New Contact Submission from {Name}"
        email_body = (
            f"You have a new message from your website's contact form:\n\n"
            f"Name: {Name}\n"
            f"Email: {Email}\n"
            f"Phone: {Phone}\n"
            f"Subject: {Subject}\n\n"
            f"Message:\n{Message}"
        )
        
        # Using f-string for a clean email format (Subject must be part of the header)
        email_text = f"Subject: {email_subject}\n\n{email_body}"

        # Connect to the SMTP server (using Gmail as an example) and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # Use encode('utf-8') to support a wider range of characters
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, email_text.encode('utf-8'))

        return {"status": "success", "message": "Form submitted successfully!"}

    except smtplib.SMTPAuthenticationError:
        print("SMTP AUTHENTICATION ERROR: The username/password is not accepted. Check SENDER_PASSWORD in .env, ensure you are using a Google App Password.")
        raise HTTPException(status_code=500, detail="Server email error: Authentication failed.")
    except Exception as e:
        # Generic catch-all for any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred. Please try again later.")

# --- Root Endpoint (for testing if the server is running) ---
@app.get("/")
def read_root():
    return {"message": "Logic Leafs API server is running"}

