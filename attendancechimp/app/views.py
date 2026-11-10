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
from django.utils import timezone
import uuid

# from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
#                      Lecture, QRCodeUpload, is_instructor, is_student,
#                      getUploadsForCourse)
from .models import (
    StudentProfile, InstructorProfile, Course, Lecture, QRCodeUpload
)
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
def new_course(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    return render(request, "app/new_course.html")

@csrf_exempt
def createCourse(request):
    # Only logged-in instructors can create courses.
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    instructor = InstructorProfile.objects.filter(
        user=request.user
    ).first()

    if instructor is None:
        return HttpResponse("Unauthorized", status=401)

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    course_name = request.POST.get("course-name", "").strip()
    start_time = request.POST.get("start-time", "").strip()
    end_time = request.POST.get("end-time", "").strip()

    days = [
        day
        for day in ("mon", "tue", "wed", "thu", "fri")
        if f"day-{day}" in request.POST
    ]

    if not course_name or not start_time or not end_time or not days:
        return HttpResponse("Missing information", status=400)

    if len(course_name) > 200:
        return HttpResponse("Course name is too long", status=400)

    if Course.objects.filter(name=course_name).exists():
        return HttpResponse("Course already exists", status=400)

    meeting_schedule = f"{', '.join(days)} {start_time}-{end_time}"

    if len(meeting_schedule) > 200:
        return HttpResponse("Schedule is too long", status=400)

    Course.objects.create(
        name=course_name,
        instructor=instructor,
        meeting_schedule=meeting_schedule,
    )

    return HttpResponse("Course created successfully", status=200)

def new_lecture(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    courses = Course.objects.all()
    return render(request, "app/new_lecture.html", {"courses": courses})


@csrf_exempt
def createLecture(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    course_name = request.POST.get("choice", "").strip()
    if not course_name:
        return HttpResponse("Missing course name", status=400)

    try:
        course = Course.objects.get(name=course_name)
    except Course.DoesNotExist:
        return HttpResponse("Course not found", status=400)
    except Course.MultipleObjectsReturned:
        return HttpResponse("Course name is not unique", status=400)

    Lecture.objects.create(
        course=course,
        date=timezone.now(),
        qr_identifier=uuid.uuid4().hex,
    )

    return HttpResponse("Lecture created successfully", status=200)

def new_qr_upload(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not StudentProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    return render(request, "app/new_qr_upload.html")


@csrf_exempt
def createQRCodeUpload(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    student = StudentProfile.objects.filter(user=request.user).first()
    if student is None:
        return HttpResponse("Unauthorized", status=401)

    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    image = request.FILES.get("imageUpload")
    if image is None:
        return HttpResponse("Missing image", status=400)

    QRCodeUpload.objects.create(
        student=student,
        image=image,
    )

    return HttpResponse("QR code uploaded successfully", status=200)

def dumpUploads(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    uploads = QRCodeUpload.objects.select_related(
        "student__user"
    ).order_by("id")

    data = [
        {
            "username": upload.student.user.username,
            "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for upload in uploads
    ]

    return JsonResponse(data, safe=False)

# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



