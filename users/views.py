from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView
import random


def homepage(request):
    return render(request, 'homepage.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})



class CustomLoginView(LoginView):
    template_name = 'login.html'



def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        method = request.POST.get("method")  # 'email' or 'sms'

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            code = str(random.randint(100000, 999999))
            request.session["mfa_code"] = code
            request.session["auth_method"] = method
            request.session["user_email"] = user.email
            request.session["user_phone"] = user.phone_number  # ✅ fixed

            if method == "email":
                send_mail(
                    "Your ABY Verification Code",
                    f"Your verification code is: {code}",
                    "noreply@aby.com",
                    [user.email],
                    fail_silently=False,
                )
            elif method == "sms":
                send_sms(user.phone_number, code)  # ✅ fixed

            return redirect("verify_mfa")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")  # ✅ fixed



@login_required
def mfa_method(request):
    if request.method == "POST":
        method = request.POST.get("method")
        code = str(random.randint(100000, 999999))
        request.session["mfa_code"] = code
        request.session["auth_method"] = method
        request.session["otp_id"] = "mocked-id"  # If using external API

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
            send_sms(user.phone_number, code)  # Replace with your actual SMS logic

        return redirect("verify_mfa")
    return render(request, "mfa_method.html")

@login_required
def verify_mfa(request):
    if request.method == "POST":
        entered_code = request.POST.get("code")
        actual_code = request.session.get("mfa_code")
        if entered_code == actual_code:
            return redirect("dashboard")
        else:
            return render(request, "verify.html", {"error": "Invalid code"})
    return render(request, "verify.html")

