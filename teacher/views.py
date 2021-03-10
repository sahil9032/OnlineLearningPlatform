import os
import uuid as uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import redirect, render

from accounts.models import *
from onlinelearningplatform import settings
from teacher.decorators import allowed_users
from teacher.forms import CreateCourseForm, AddLessonForm
from tmp.convert import convert

resolution = ['720', '480', '360', '240', '144']
Link = 'https://storage.googleapis.com/e-learning-2a88b.appspot.com/'

from google.cloud import storage


def upload_blob(source_file_name, destination_blob_name):
    storage_client = storage.Client.from_service_account_json('keys.json')
    bucket = storage_client.bucket('e-learning-2a88b.appspot.com')
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


def validator(request, course):
    course = Course.objects.filter(id=course)
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
    return render(request, 'teacher/coursedetail.html', context={'course': course, 'lessons': lessons})


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
            filename = key + request.FILES['file'].name
            file = request.FILES['file'].read()
            location = os.path.join(str(settings.BASE_DIR), 'tmp')
            location = os.path.join(location, filename)
            with open(location, 'wb') as temp_file:
                temp_file.write(file)
            outputs = []
            uploads = []
            for i in resolution:
                outputs.append(key + '_' + i + '.mp4')
            for i in range(len(outputs)):
                if convert(filename, outputs[i], resolution[i]) == 0:
                    path = os.path.join(str(settings.BASE_DIR), 'tmp')
                    path = os.path.join(path, outputs[i])
                    uploads.append([path, outputs[i]])
            os.remove(location)
            for i in uploads:
                upload_blob(i[0], i[1])
                os.remove(i[0])
            lesson = Lesson(title=request.POST['title'],
                            content=request.POST['content'],
                            course_id=courseid,
                            video_720p=Link + key + '_' + '720.mp4',
                            video_480p=Link + key + '_' + '480.mp4',
                            video_360p=Link + key + '_' + '360.mp4',
                            video_240p=Link + key + '_' + '240.mp4',
                            video_144p=Link + key + '_' + '144.mp4', )
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
    if lesson is None or lesson.count() == 0:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    return render(request, 'teacher/lessondetail.html', context={'lesson': lesson[0]})
