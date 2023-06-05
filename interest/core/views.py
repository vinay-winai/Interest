from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import User,Interest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

@login_required
def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        state = data.get('state')
        if state == 'on':
            message = "off"
        else:
            message = "On"
        return JsonResponse({"success": True, "message": message})
    return render(request, "interest/index.html")
@login_required
def cindex(request):
    return render(request, "interest/cindex.html")
@login_required
def room(request, room_name):
    return render(request, "interest/room.html", {"room_name": room_name})

def login_view(request):
    """User login_page."""
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "interest/login.html", {
            "message": "Invalid credentials."
        })
    return render(request, "interest/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    """New user registration page."""
    interests_list = Interest.objects.all()
    print(interests_list)
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        phone = request.POST["phone"]
        country = request.POST["country"]
        gender = request.POST["gender"]
        interests = request.POST.getlist("interests[]")
        try:
            validate_password(password, username)
        except ValidationError as e:
            return render(request, "interest/register.html", {
                "message":e,
                "interests_list":interests_list,
                })
        confirmation = request.POST["confirmation"]
        x_check = password != confirmation
        d_check = email and password and username and phone and country and gender and interests 
        if not d_check or x_check:
            message = "Atleast one field is empty."
            if x_check:
                message = "Passwords must match."
            return render(request, "interest/register.html", {
                "message": message,
                "interests_list":interests_list,
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username = username, email = email, password = password, phone = phone, country = country, gender = gender)
            user.save()
            selected_interests = Interest.objects.filter(name__in=interests)
            user.interests.set(selected_interests)
        except IntegrityError:
            return render(request, "interest/register.html", {
                "message": "unique values already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "interest/register.html", {"interests_list":interests_list})
