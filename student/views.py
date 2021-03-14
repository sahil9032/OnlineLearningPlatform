# Create your views here.
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import redirect, render

from accounts.models import *
from student.decorators import allowed_users


def validator(request, courseid):
    course = Course.objects.filter(id=courseid)
    if course is None or course.count() == 0:
        return False, HttpResponseNotFound('<h1>Page not found</h1>')
    course = course[0]
    enrollments = Enrollment.objects.filter(course_id=courseid).values_list('user_id', flat=True)
    if request.user.id not in enrollments:
        return False, HttpResponse('You are not authorized to view this page')
    return True, course


@login_required(login_url='/accounts/login')
def logoutUser(request):
    logout(request)
    return redirect('/accounts/login')


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def getCourses(request):
    enrollment = request.user.enrollment_set.values_list('course_id')
    enrolled_courses = Course.objects.filter(pk__in=enrollment)
    return render(request, 'student/index.html', context={'courses': enrolled_courses})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def enrollInCourse(request):
    courses = Course.objects.all()
    enrollment = request.user.enrollment_set.values_list('course_id')
    enrolled_courses = Course.objects.filter(pk__in=enrollment)
    available_courses = courses.difference(enrolled_courses)
    if request.method == 'POST':
        for course in enrolled_courses:
            if course.id == request.POST['course_id']:
                messages.info(request, 'You\'re already enrolled in course.')
        else:
            enrollment = Enrollment(course_id=request.POST['course_id'], user_id=request.user.id)
            enrollment.save()
            redirect('/student/')

    return render(request, 'student/enroll.html', context={'courses': available_courses})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def getCourseDetail(request, courseid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    course = response
    lessons = course.lesson_set.all()
    return render(request, 'student/coursedetail.html', context={'course': course, 'lessons': lessons})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def getLessonDetail(request, courseid, lessonid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    lesson = Lesson.objects.filter(id=lessonid)
    if lesson is None or lesson.count() == 0 or str(lesson[0].course.id) != courseid:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    return render(request, 'student/lessondetail.html', context={'lesson': lesson[0]})
