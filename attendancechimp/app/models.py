"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""

from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
class InstructorProfile(models.Model):
    """Each instructor has a user account and can teach courses."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class StudentProfile(models.Model):
    """Each student has a user account and can enroll in courses."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Course

class Course(models.Model):
    """
    Stores information about a course.
    Each course has one instructor, but an instructor can teach multiple courses.
    """
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE)
    meeting_schedule = models.CharField(max_length=200)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Enrollment
class Enrollment(models.Model):
    """
    Connects students to courses.
    A student can take multiple courses, and a course can have many students.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Lecture
class Lecture(models.Model):
    """
    Stores each class meeting for a course.
    Each lecture has a date and a unique QR code for attendance.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField()
    qr_identifier = models.CharField(max_length=100, unique=True)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# QR Code Upload
class QRCodeUpload(models.Model):
    """
    Stores QR code images uploaded by students.
    Each upload belongs to a student and may be linked to a lecture.
    """
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to="qr_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



