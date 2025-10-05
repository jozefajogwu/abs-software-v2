from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import resend
from django.conf import settings

def generate_activation_link(user):
    token = PasswordResetTokenGenerator().make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return f"http://yourdomain.com/api/auth/activate/{uid}/{token}/"


resend.api_key = settings.RESEND_API_KEY

def send_resend_email(to, subject, html_content):
    params = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": to,
        "subject": subject,
        "html": html_content
    }
    return resend.Emails.send(params)