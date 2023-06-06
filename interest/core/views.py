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

user_online_status = {}

@login_required
def index(request):
    user_id = request.user.id
    if request.method == "POST":
        data = json.loads(request.body)
        state = data.get('state')
        if state == 'on':
            message = "On"
            user_online_status[user_id] = 0
        else:
            user_online_status[user_id] = 1
            message = "Off"
        return JsonResponse({"success": True, "message": message})
    user_online_status[user_id] = 1
    return render(request, "interest/index.html")

@login_required
def connect(request):
    user = request.user
    room_name = user.username
    interests = user.interests.all()
    user_status = user_online_status.get(user.id,-1)
    print("status",user_status,room_name)
    if user_status not in [0,1,-1]:
        if not user_status.endswith('#'):
            room_name = user_status + room_name
            user_online_status[user.id] = 0
        print("status1",user_status,room_name) 
    common_interest_users = User.objects.filter(interests__in=interests).exclude(id=user.id).distinct()
    print("status2",common_interest_users)
    for common_interest_user in common_interest_users:
        if user_online_status.get(common_interest_user.id) ==1 and common_interest_user.is_authenticated:
            room_name+= common_interest_user.username
            user_online_status[common_interest_user.id] = user.username
            print("status3",room_name)
            break
    if not common_interest_users or room_name==user.username:
        for user_online_status_key in user_online_status:
            if user_online_status_key == user.id:
                continue
            if user_online_status.get(user_online_status_key)==1 and User.objects.get(id=user_online_status_key).is_authenticated:
                room_name+= User.objects.get(id=user_online_status_key).username
                user_online_status[user_online_status_key] = user.username +'#'
                print("status4",room_name)
                break
    if room_name!=user.username:
        user_online_status[user.id] = 0
        return render(request, "interest/room.html", {"room_name": room_name,"user_name": user.username})
    if user_status not in [0,1,-1]:
        room_name = user_status[:-1] + room_name
        return render(request, "interest/room.html", {"room_name": room_name,"user_name": user.username})
    return JsonResponse({"success": True, "message": "No users found."})

def get_other_user_details(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        user = User.objects.get(username=username)
        interests = user.interests.all()
        interests = [interest.name for interest in interests]
        interests = ",".join(interests)
        user_details = {"username": user.username,"country": user.country, "gender": user.gender, "interests": interests}
        return JsonResponse({"success": True, "user_details": user_details})
    return JsonResponse({"success": False})

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
                "message": "unique values already taken.",
                "interests_list":interests_list,
            })
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(reverse("index"))
    return render(request, "interest/register.html", {"interests_list":interests_list})
