from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=200, null=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_on = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False)
    content = models.CharField(max_length=100000, null=False)
    videoPath = models.CharField(max_length=200, null=False, default="")

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.id


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False)
    content = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.title


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=False)
    link = models.CharField(max_length=200, null=False)
    grade = models.IntegerField(default=1,
                                validators=[
                                    MaxValueValidator(100),
                                    MinValueValidator(1)
                                ])

    def __str__(self):
        return str(self.id)
