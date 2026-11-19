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
def getUploads(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Unauthorized", status=401)

    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)

    course = request.GET.get("course", "").strip()
    if not course:
        return JsonResponse({"error": "Missing course parameter"}, status=400)

    uploads = getUploadsForCourse(course)
    data = [
        {
            "username": upload.student.user.username,
            "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for upload in uploads
    ]
    return JsonResponse(data, safe=False)