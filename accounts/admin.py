from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Submission)
