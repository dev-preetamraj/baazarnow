import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
import random
from .models import (
    Profile
)
from .decorators import (
    unauthenticated_user,
    allowed_users,
    email_verified_user
)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

@unauthenticated_user
def register_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        user_type = request.POST.get('user_type')
        qs = User.objects.filter(username__iexact=username)
        if qs.exists():
            messages.error(request, "User with this username already exists.")
        qs = User.objects.filter(email__iexact=email)
        if qs.exists():
            messages.error(request, "User with this email already exists.")
        if password1!=password2:
            messages.error(request, "Password did not matched.")
        if len(password1)<8:
            messages.error(request, "Password must be 8 characters(or more) long.")
        try:
            user = User.objects.create_user(username, email, password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            if user_type=='supplier':
                set_group = Group.objects.get(name='supplier')
                user.groups.add(set_group)
            else:
                set_group = Group.objects.get(name='consumer')
                user.groups.add(set_group)
            _profile = Profile.objects.create(user=user)
            _profile.gender = gender
            email_otp = random.randint(111111,999999)
            _profile.email_otp = email_otp
            _profile.save()
            if(_profile.is_email_verified):
                login(request, user)
                return redirect('supplier_index')
            else:
                send_email_verification_mail(email_otp, email)
                login(request, user)
                return redirect('email_verification_view')

        except Exception as e:
            user = None
            print(e)
            messages.error(request, "Something went wrong. Try after sometime. We are working on it.")

    context = {}
    return render(request, 'accounts/register.html', context)

def send_email_verification_mail(email_otp, email_to):
    subject = "Email verification for baazarnow.com"
    message = f"OTP for verification is: {email_otp}.\nOR\nClick here to vigit the verification page: https://istp-app.herokuapp.com{reverse(email_verification_view)}\n\nThank and Regards!\nbaazarnow.com"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email_to], fail_silently=False)

def edit_email_view(request):
    user = request.user
    if(request.method == 'POST'):
        email = request.POST.get('email')
        user.email = email
        user.save()
        profile = user.profile
        email_otp = random.randint(111111,999999)
        profile.email_otp = email_otp
        profile.save()
        send_email_verification_mail(email_otp, email)
        return redirect('email_verification_view')
    return render(request, 'accounts/edit_email.html', {})

@login_required
def email_verification_view(request):
    profile = request.user.profile
    if(request.method == 'POST'):
        email_otp = request.POST.get('email_otp')
        if profile.email_otp == email_otp:
            profile.is_email_verified = True
            profile.save()
            messages.success(request, "Email is verified")
            return redirect('supplier_index')
        else:
            messages.error(request, "Please enter the correct otp!")
    return render(request, 'accounts/email_otp.html', {})

@csrf_exempt
@login_required
def initiate_email_verification(request):
    user = request.user
    profile = user.profile
    email_otp = random.randint(111111,999999)
    profile.email_otp = email_otp
    profile.save()
    email_to = user.email
    send_email_verification_mail(email_otp, email_to)
    messages.success(request, "OTP sent, check your email.")
    return redirect('email_verification_view')

@unauthenticated_user
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        authenticated_user = authenticate(username=username, password=password)
        if authenticated_user is not None:
            login(request, authenticated_user)
            messages.success(request, f"Logged in as {username}")
            return redirect('dashboard')
        else:
            messages.error(request, "Username or Password is incorrect.")
    context = {}
    return render(request, 'accounts/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('supplier_index')

def send_password_reset_mail(email_token, email_to):
    subject = "Password reset for baazarnow.com"
    message = f"Please click on the given link to reset your password.\nReset Link: https://istp-app.herokuapp.com/accounts/reset_password/{email_token}\n\nThank and Regards!\nbaazarnow.com"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, [email_to], fail_silently=False)

@unauthenticated_user
def forgot_password_view(request):
    if(request.method == 'POST'):
        email = request.POST.get('email')
        try:
            profile = User.objects.get(email=email).profile
            reset_password_token = uuid.uuid4()
            profile.reset_password_token = reset_password_token
            profile.save()
            send_password_reset_mail(reset_password_token, email)
            messages.success(request, "Email sent with a link to reset password.")
        except Exception as e:
            messages.success(request, "We didn't find the account with this email.")
            print(e)
    return render(request, 'accounts/forgot_password.html', {})

@unauthenticated_user
def reset_password_view(request, email_token):
    try:
        user = Profile.objects.get(reset_password_token = email_token).user
        if(request.method=='POST'):
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if(password1 =='' or password2==''):
                messages.warning(request, 'Please enter your new password to proceed.')
            elif(password1!=password2):
                messages.warning(request, "Password did not matched.")
            else:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('login')
        print(user)
    except Exception as e:
        print(e)
    return render(request, 'accounts/reset_password.html', {})

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'accounts/settings.html', context)


@login_required
def update_profile(request):
    user = request.user
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        if(gender=="choose"):
            gender = user.profile.gender
        adrs_line_1 = request.POST.get('adrs_line_1')
        adrs_line_2 = request.POST.get('adrs_line_2')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        phone_number = request.POST.get('phone_number')
        aadhar_number = request.POST.get('aadhar_number')
        pan_number = request.POST.get('pan_number')
        try:
            profile = Profile.objects.get(user=user)
            user.first_name = first_name
            user.last_name = last_name
            profile.gender = gender                
            profile.adrs_line_1 = adrs_line_1
            profile.adrs_line_2 = adrs_line_2
            profile.city = city
            profile.district = district
            profile.state = state
            profile.country = country
            profile.postal_code = postal_code
            profile.phone_number = phone_number
            profile.aadhar_number = aadhar_number
            profile.pan_number = pan_number
            user.save()
            profile.save()
            messages.success(request, "Profile updated successfully...")
            return redirect('profile_view')
        except:
            messages.success(request, "Something went wrong...")
            return redirect('profile_view')

@csrf_exempt
@login_required
def update_profile_pic(request):
    user = request.user
    image = request.FILES.get('image')
    print(type(image))
    try:
        profile = Profile.objects.get(user=user)
        profile.profile_pic = image
        profile.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")