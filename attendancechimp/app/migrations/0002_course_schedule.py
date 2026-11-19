from django.db import migrations, models
from django.utils.dateparse import parse_time


def copy_course_schedules(apps, schema_editor):
    Course = apps.get_model("app", "Course")
    courses = Course.objects.using(schema_editor.connection.alias)
    reserved_numbers = set(courses.values_list("name", flat=True))
    used_numbers = set()
    weekdays = ("mon", "tue", "wed", "thu", "fri")

    for course in courses.order_by("pk").iterator():
        number = course.name
        suffix = course.pk
        while not number or number in used_numbers:
            ending = f"-{suffix}"
            number = f"{course.name[:200 - len(ending)]}{ending}"
            if number in reserved_numbers:
                number = ""
            suffix += 1
        used_numbers.add(number)
        course.course = number

        days, _, hours = course.meeting_schedule.rpartition(" ")
        meeting_days = {day.strip() for day in days.split(",")}
        start, _, end = hours.partition("-")
        try:
            course.start_time = parse_time(start)
            course.end_time = parse_time(end)
        except ValueError:
            course.start_time = course.end_time = None

        for day in weekdays:
            setattr(course, day, day in meeting_days)
        course.save(update_fields=["course", "start_time", "end_time", *weekdays])


class Migration(migrations.Migration):
    dependencies = [("app", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="course",
            name="course",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="course",
            name="start_time",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="course",
            name="end_time",
            field=models.TimeField(blank=True, null=True),
        ),
        *[
            migrations.AddField(
                model_name="course",
                name=day,
                field=models.BooleanField(default=False),
            )
            for day in ("mon", "tue", "wed", "thu", "fri")
        ],
        migrations.RunPython(copy_course_schedules, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="course",
            name="course",
            field=models.CharField(max_length=200, unique=True),
        ),
    ]