"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)
from .models import StudentProfile, InstructorProfile
CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    current_time = datetime.now(CDT).strftime("%H:%M")
    context = {
        "current_time": current_time,
        "logged_in_user": request.user if request.user.is_authenticated else None
    }
    return render(request, "app/index.html", context)

def time_view(request):
    current_time = datetime.now(CDT).strftime("%H:%M")
    return HttpResponse(current_time, content_type="text/plain")


def sum_view(request):
    n1 = float(request.GET["n1"])
    n2 = float(request.GET["n2"])
    return HttpResponse(f"<p>{n1+n2}</p>")



# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------
def new(request):
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    return render(request, "app/new.html")

@csrf_exempt
def createUser(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    email = request.POST.get("email")
    user_name = request.POST.get("user_name")
    password = request.POST.get("password")
    is_student = request.POST.get("is_student")

    if not email or not user_name or not password or is_student not in ("0", "1"):
        return HttpResponse("Missing information", status=400)

    if User.objects.filter(email__iexact=email).exists():
        return HttpResponse("Email already exists", status=400)

    if User.objects.filter(username=user_name).exists():
        return HttpResponse("Username already exists", status=400)

    user = User.objects.create_user(
        username=user_name,
        email=email,
        password=password
    )

    if is_student == "1":
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)

    login(request, user)

    return HttpResponse("User created successfully")

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



