from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UserSerializer, RoleSerializer
from .utils import generate_activation_link

import random

# ────────────────────────────────────────────────────────────────
# Basic Views
# ────────────────────────────────────────────────────────────────

def homepage(request):
    return render(request, 'homepage.html')

def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        method = request.POST.get("method")  # 'email' or 'sms'

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            code = str(random.randint(100000, 999999))
            request.session.update({
                "mfa_code": code,
                "auth_method": method,
                "user_email": user.email,
                "user_phone": user.phone_number,
            })

            if method == "email":
                send_mail(
                    "Your ABY Verification Code",
                    f"Your verification code is: {code}",
                    "noreply@aby.com",
                    [user.email],
                    fail_silently=False,
                )
            elif method == "sms":
                send_sms(user.phone_number, code)

            return redirect("verify_mfa")
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

@login_required
def mfa_method(request):
    if request.method == "POST":
        method = request.POST.get("method")
        code = str(random.randint(100000, 999999))
        request.session.update({
            "mfa_code": code,
            "auth_method": method,
            "otp_id": "mocked-id",
        })

        user = request.user
        if method == "email":
            send_mail(
                "Your ABY Verification Code",
                f"Your code is: {code}",
                "noreply@aby.com",
                [user.email],
                fail_silently=False,
            )
        elif method == "sms":
            send_sms(user.phone_number, code)

        return redirect("verify_mfa")
    return render(request, "mfa_method.html")

@login_required
def verify_mfa(request):
    if request.method == "POST":
        entered_code = request.POST.get("code")
        actual_code = request.session.get("mfa_code")
        if entered_code == actual_code:
            return redirect("dashboard")
        return render(request, "verify.html", {"error": "Invalid code"})
    return render(request, "verify.html")

# ────────────────────────────────────────────────────────────────
# API Views
# ────────────────────────────────────────────────────────────────

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": getattr(user, 'role', 'N/A')
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_roles(request):
    roles = [
        {"key": key, "label": label}
        for key, label in CustomUser._meta.get_field('role').choices
    ]
    return Response(roles)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    print("Request method:", request.method)  # ✅ Move this to the top

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save(is_active=False)
        send_activation_email(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, id):
    try:
        user = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    user.is_active = False
    user.save()
    return Response({"detail": "User deactivated"}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    total = CustomUser.objects.count()
    active = CustomUser.objects.filter(is_active=True).count()
    inactive = CustomUser.objects.filter(is_active=False).count()
    employees = CustomUser.objects.exclude(role__isnull=True).count()
    return Response({
        "total_users": total,
        "active_users": active,
        "inactive_users": inactive,
        "employees": employees
    })

@api_view(['GET'])
def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response({"detail": "Invalid activation link"}, status=400)

    if PasswordResetTokenGenerator().check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"detail": "Account activated successfully"})
    return Response({"detail": "Invalid or expired token"}, status=400)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_role(request):
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ────────────────────────────────────────────────────────────────
# Utility
# ────────────────────────────────────────────────────────────────

def send_activation_email(user):
    activation_link = generate_activation_link(user)
    subject = "Activate Your ABY Account"
    message = f"Hi {user.username},\n\nPlease activate your account using the link below:\n{activation_link}\n\nThanks,\nABY Team"
    send_mail(subject, message, None, [user.email])
