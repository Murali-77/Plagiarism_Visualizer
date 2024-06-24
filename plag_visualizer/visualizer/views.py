from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
import matplotlib.pyplot as plt
import io
import urllib, base64
import numpy as np
from django.shortcuts import render

from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import random
from django.contrib.auth.models import User

# sign-up otp logic
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):

    email_message = EmailMessage(
        'your OTP verification Code',
        f'your otp code is {otp}',
        settings.EMAIL_HOST_USER,
        [email]
    )

    email_message.send()

def signup(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        otp = generate_otp()

        request.session['signup_data'] = {
            'username': username,
            'password': password,
            'email': email,
             'otp': otp
        }

        send_otp_email(email, otp)
        return redirect('verify_otp')
    return render(request, 'signup.html')


def verify_otp_view(request):

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        signup_data = request.session.get('signup_data')

        if signup_data and signup_data['otp'] == entered_otp:
            User.objects.create_user(
                username=signup_data['username'],
                password=signup_data['password'],
                email=signup_data['email']
            )
            return redirect('login')
        else:
            return render(request, 'verify_otp.html', {'error_message': 'Invalid OTP'})

    return render(request, 'verify_otp.html')

# login and logout pages' logic
def login_page(request):

    if request.user.is_authenticated:
        return redirect("home")

    error_message = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = 'invalid login credentials'

    return render(request, 'login.html', {'error_message': error_message})

def logout_page(request):
    logout(request)
    return redirect('login')

# Plagiarism visualization logic
def calculate_similarity(text1, text2):
    # A simple similarity measure: Jaccard similarity
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    similarity = len(intersection) / len(union) if union else 0
    return similarity


def plot_similarity(similarity):

    labels = f'similar : {round(similarity,3)}', f'non-similar : {round(1-similarity,3)}'
    sizes = [similarity, 1-similarity]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=90)
    ax.axis('equal')

    # ax.bar(['Similarity'], [similarity])
    # ax.bar(['Non-similarity'], [1-similarity])
    # ax.set_ylim(0, 1)
    # ax.set_ylabel('Similarity')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode()
    uri = urllib.parse.quote(string)
    buf.seek(0)
    return [uri,buf]


# function that carries email logic
def email_sender(recipient_email, chart_buffer):
    email = EmailMessage(
        'Your Text Similarity Chart',
        'Please find attached the similarity chart for your text inputs.',
        settings.EMAIL_HOST_USER,
        [recipient_email]
    )
    email.attach('similarity_chart.png', chart_buffer.getvalue(), 'image/png')
    email.send()


# Main function url = 'home' .
@login_required(login_url='/main/')
def home(request):
    message = "nil"
    similarity = 0
    plot_url = None
    email_sent = False

    if request.method == 'POST':
        text1 = request.POST.get('text1')
        text2 = request.POST.get('text2')
        email = request.POST.get('email')

        if text1 and text2 and email:
            similarity = calculate_similarity(text1, text2)
            plot_url = plot_similarity(similarity)[0]
            chart_buffer = plot_similarity(similarity)[1]

            # Calculating plagiarism percentage .

            text1_data = text1.split(' ')
            text2_data = text2.split(' ')

            s = set()

            for i in text1_data:
                for j in text2_data:
                    if i == j:
                        s.add(i)

            message = str((len(s)/len(text1_data)) * 100)

            print('common words : ', s)
            print('count        : ', len(s))
            print('ratio        : ', (len(s) / len(text1_data)) * 100)
            print('-' * 100)

        else:
            message = 'nil'

        email_sender(email, chart_buffer)
        email_sent = True

    return render(request, 'index.html', {'message': message, 'plot_url': plot_url, 'similarity': similarity, 'email_sent': email_sent})

