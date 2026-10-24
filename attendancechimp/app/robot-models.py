
# LLM: ChatGPT (GPT-6)
# Prompt: Create Django models for an attendance tracking app.
# Include instructor and student profiles, courses, enrollments,
# lectures, and QR code uploads. Add simple ways to prevent
# duplicate enrollments and track verified attendance.

from django.db import models
from django.contrib.auth.models import User


class InstructorProfile(models.Model):
    """Stores an instructor's account information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class StudentProfile(models.Model):
    """Stores a student's account information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Course(models.Model):
    """Stores courses and their assigned instructors."""
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    meeting_schedule = models.CharField(max_length=200)


class Enrollment(models.Model):
    """Keeps track of which students are enrolled in each course."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "course")


class Lecture(models.Model):
    """Stores each lecture and its unique QR code."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_identifier = models.CharField(max_length=100, unique=True)


class QRCodeUpload(models.Model):
    """Stores uploaded QR code images and their verification status."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(upload_to="qr_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)