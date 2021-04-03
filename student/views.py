# Create your views here.
import os
import uuid

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import redirect, render
from google.cloud import storage

from accounts.models import *
from onlinelearningplatform import settings
from student.decorators import allowed_users
from student.forms import CreateSubmissionForm

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(str(settings.BASE_DIR), 'keys.json')


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client().from_service_account_json('keys.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


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
    assignment = course.assignment_set.all()
    return render(request, 'student/coursedetail.html',
                  context={'course': course, 'lessons': lessons, 'assignment': assignment})


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


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def getAssignmentDetail(request, courseid, assignmentid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    assignment = Assignment.objects.filter(id=assignmentid)
    if assignment is None or assignment.count() == 0 or str(assignment[0].course.id) != courseid:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    assignment = assignment[0]
    form = CreateSubmissionForm()
    if request.method == 'POST':
        form = CreateSubmissionForm(files=request.FILES)
        if form.is_valid():
            key = str(uuid.uuid4())
            filename = request.FILES['file'].name
            filename = key + '.' + list(map(str, filename.split('.')))[-1]
            location1 = os.path.join(str(settings.BASE_DIR), 'tmp')
            location2 = os.path.join(location1, filename)
            file = request.FILES['file']
            with open(location2, 'wb+') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
            upload_blob('e-learning-2a88b.appspot.com', os.path.join(location1, filename),
                        filename)
            os.remove(os.path.join(location1, filename))
            submission = Submission(user_id=request.user.id,
                                    assignment_id=assignmentid,
                                    link='https://storage.googleapis.com/e-learning-2a88b.appspot.com/' + filename)
            submission.save()
            return redirect('/student/course/' + courseid)
    return render(request, 'student/assignmentdetail.html',
                  context={'assignment': assignment, 'form': form})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['student'])
def getSubmissions(request):
    submissions = request.user.submission_set.all()
    return render(request, 'student/submissions.html',
                  context={'submissions': submissions})
