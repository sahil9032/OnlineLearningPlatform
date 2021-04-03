import django

django.setup()
import base64
import os
import shutil
import uuid as uuid
from multiprocessing import Process

import ffmpeg_streaming
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import redirect, render
from google.cloud import storage

from accounts.models import *
from onlinelearningplatform import settings
from teacher.decorators import allowed_users
from teacher.forms import CreateCourseForm, AddLessonForm, AddAssignmentForm

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(str(settings.BASE_DIR), 'keys.json')


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client().from_service_account_json('keys.json')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def upload(filename, location1, location2, key):
    video = ffmpeg_streaming.input(location2)
    hls = video.hls(ffmpeg_streaming.Formats.h264())
    hls.auto_generate_representations()
    hls.output(os.path.join(os.path.join(location1, key), 'master.m3u8'))
    os.remove(location2)
    for file in os.listdir(os.path.join(location1, key)):
        upload_blob('e-learning-2a88b.appspot.com', os.path.join(os.path.join(location1, key), file), key + '/' + file)
    shutil.rmtree(os.path.join(location1, key))


def validator(request, courseid):
    course = Course.objects.filter(id=courseid)
    if course is None or course.count() == 0:
        return False, HttpResponseNotFound('<h1>Page not found</h1>')
    course = course[0]
    if course.created_by.username != request.user.username:
        return False, HttpResponse('You are not authorized to view this page')
    return True, course


@login_required(login_url='/accounts/login')
def logoutUser(request):
    logout(request)
    return redirect('/accounts/login')


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def getCourses(request):
    courses = request.user.course_set.all()
    return render(request, 'teacher/index.html', context={'courses': courses})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def createCourse(request):
    form = CreateCourseForm()
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        form = CreateCourseForm({'created_by': request.user.id,
                                 'title': title,
                                 'description': description})
        if form.is_valid():
            form.save()
            return redirect('/teacher')
    return render(request, 'teacher/createcourse.html', context={'form': form})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def getCourseDetail(request, courseid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    course = response
    lessons = course.lesson_set.all()
    assignment = course.assignment_set.all()
    return render(request, 'teacher/coursedetail.html',
                  context={'course': course, 'lessons': lessons, 'assignment': assignment})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def addLesson(request, courseid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    form = AddLessonForm()
    if request.method == 'POST':
        form = AddLessonForm({'title': request.POST['title'], 'content': request.POST['content']}, request.FILES)
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
            p = Process(target=upload, args=(filename, location1, location2, key))
            p.start()
            message = 'https://storage.googleapis.com/e-learning-2a88b.appspot.com/' + key + '/master.m3u8'
            message_bytes = message.encode('ascii')
            encode = str(base64.b64encode(message_bytes))
            embedLink = 'https://andhaetg.github.io/universalplyr/player.html?' + encode[2:len(encode) - 1]
            lesson = Lesson(title=request.POST['title'],
                            content=request.POST['content'],
                            course_id=courseid,
                            videoPath=embedLink)
            lesson.save()
            return redirect('/teacher/course/' + courseid)
    return render(request, 'teacher/addlesson.html', context={'form': form})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def getLessonDetail(request, courseid, lessonid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    lesson = Lesson.objects.filter(id=lessonid)
    if lesson is None or lesson.count() == 0 or str(lesson[0].course.id) != courseid:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    return render(request, 'teacher/lessondetail.html', context={'lesson': lesson[0]})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def addAssignment(request, courseid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    form = AddAssignmentForm()
    if request.method == 'POST':
        form = AddAssignmentForm({'title': request.POST['title'], 'content': request.POST['content']})
        if form.is_valid():
            assignment = Assignment(title=request.POST['title'],
                                    content=request.POST['content'],
                                    course_id=courseid)
            assignment.save()
            return redirect('/teacher/course/' + courseid)
    return render(request, 'teacher/addassignment.html', context={'form': form})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def getAssignmentDetail(request, courseid, assignmentid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    assignment = Assignment.objects.filter(id=assignmentid)
    if assignment is None or assignment.count() == 0 or str(assignment[0].course.id) != courseid:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    assignment = assignment[0]
    submissions = assignment.submission_set.all()
    return render(request, 'teacher/assignmentdetail.html',
                  context={'assignment': assignment, 'submissions': submissions, 'course': valid})


@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['teacher'])
def getStudentDetail(request, courseid):
    valid, response = validator(request, courseid)
    if not valid:
        return response
    course = response
    enrollments = course.enrollment_set.values_list('user_id')
    students = User.objects.filter(pk__in=enrollments)
    return render(request, 'teacher/students.html', context={'students': students, 'course': course})
