from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django import forms
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse

from .forms import UserRegisterForm, ActivationForm, LoginForm
from .models import Subscriber
from .tokens import account_activation_token

# sendgrid mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import random


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if User.objects.filter(email=email).exists():
                messages.warning(request, 'User with this email already exists!', extra_tags='email')
                return redirect(reverse('register'))
            else:
                user = form.save(commit=False)
                user.is_active = False
                user.save()   

                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                content = render_to_string('user/activate_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                message = Mail(
                    from_email='alimardan_akhmedov@hotmail.com',
                    to_emails=form.cleaned_data.get('email'),
                    subject=mail_subject,
                    html_content=content
                )

                try:
                    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e.body)

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            return render(request, 'user/alert.html')

    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }    

    return render(request, 'user/register.html', context)


def login_view(request):
    if request.method == "POST":
        login_form = LoginForm(request.POST or None)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if login_form.is_valid():
            user = login_form.login(request)
            if user is not None and user.is_active:
                login(request, user)
                return redirect(reverse('home'))
        else:
            messages.warning(request, 'Password or username is not correct!', extra_tags="login")
            return redirect(reverse('login_view'))
    else:
        login_form = LoginForm()

    context = {
        'login_form': LoginForm()
    }

    return render(request, 'user/login.html', context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'user/confirmation.html')
    else:
        return render(request, 'user/denied.html')


def alert(request):
    return render(request, 'user/alert.html')


def random_digits():
    return "%0.12d" % random.randint(0, 999999999999)

def send_activation_mail(request):
    if request.method == 'POST':
        activation_form = ActivationForm(request.POST or None)

        if activation_form.is_valid():
            email = activation_form.cleaned_data.get('email')

            try:
                selected_user = User.objects.get(email=email)
                sub = Subscriber(email=request.POST['email'], conf_num=random_digits(), user=selected_user)
                sub.save()

                message = Mail(
                    from_email='alimardan_akhmedov@hotmail.com',
                    to_emails=sub.email,
                    subject='Account Confirmation',
                    html_content='Thank you for signing up to our newsletter! \
                        To view new posts and updates,\
                        please complete the process by \
                        <a href="{}?email={}&conf_num={}"> clicking here to \
                        confirm your registration</a>.'.format(request.build_absolute_uri('/confirm/'), sub.email, sub.conf_num)
                )

                try:
                    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e.message)

                return redirect(reverse('alert'))    

            except ObjectDoesNotExist:
                messages.warning(request, 'You entered a invalid email. Please try again with your registered email!')    
    
    return redirect(reverse('home'))


def confirm(request):
    email = request.GET['email']
    selected_user = User.objects.get(email=email)
    sub = Subscriber.objects.get(email=request.GET['email'], user=selected_user)
    if sub.conf_num == request.GET['conf_num']:
        sub.confirmed = True
        sub.save()
        return render(request, 'user/confirmation.html', {'email': sub.email, 'action': 'confirmed'})
    else:
        return render(request, 'user/denied.html', {'email': sub.email, 'action': 'denied'})