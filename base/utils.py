

from django.core.mail import send_mail
import random
from twilio.rest import Client
import random
from django.core.cache import cache
from django.conf import settings
from dotenv import load_dotenv
import os
load_dotenv()

def send_otp(email):
    otp = random.randint(100000, 999999)  
    subject = 'Your OTP for Email Verification'
    message = f'Your OTP is {otp}. Please verify your email to continue.'
    send_mail(subject, message, 'your_email@example.com', [email])
    return otp


OTP_CACHE = {}  

ACCOUNT_SID = os.getenv("ACCOUNT_SID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_sms(contact_number, message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=f"+91{contact_number}"
        )
        print(f"SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
 
def send_email_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    # send_mail(subject, message, 'your_email@example.com', [email])
    send_mail(subject, message,from_email,recipient_list)  
  
def generate_otp(employee, option):
    otp = random.randint(1000, 9999)
    formatted_number = f"+91{employee.contact_number}"
    OTP_CACHE[formatted_number] = otp
    print("OTP_CACHE:", OTP_CACHE)
    cache.set(formatted_number, otp, timeout=300) 
    # Send OTP via SMS or Email (example)
    if option == "mobile":
        send_sms(employee.contact_number, f"Your OTP is {otp}")
    elif option == "email":
        send_email_otp(employee.email, otp)
        # send_email_otp("santhiya.b@sece.ac.in", otp)
    return {"message": "OTP sent successfully.","OTP":otp}       
# def generate_otp(employee):
#     otp = random.randint(1000, 9999)
#     formatted_number = f"+91{employee.contact_number}"
#     OTP_CACHE[formatted_number] = otp
#     print("OTP_CACHE:", OTP_CACHE)
#     cache.set(formatted_number, otp, timeout=300) 
#     # Send OTP via SMS or Email (example)
#     send_sms(employee.contact_number, f"Your OTP is {otp}")
#     return {"message": "OTP sent successfully.","OTP":otp}

def verify_otp(contact_number, otp):
    formatted_number = f"+91{contact_number}"
    
    stored_otp = cache.get(formatted_number)
    if str(stored_otp) == str(otp):
        # ✅ Remove OTP from cache after successful verification
        # cache.delete(formatted_number)
        return True
    return False


def handle_login(email, password):
    from django.contrib.auth import authenticate
    user = authenticate(username=email, password=password)
    if user is not None:
        if not user.is_active:
            return None, {"error": "Account not approved by admin."}, 403
        return user, None, None
    return None, {"error": "Invalid credentials."}, 401