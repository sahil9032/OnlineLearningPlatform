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


def upload(filename, location):
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("credentials.txt")
    drive = GoogleDrive(gauth)
    f = drive.CreateFile({
        'title': filename,
        'parents': [{
            'kind': 'drive#fileLink',
            'teamDriveId': '0ADLW2N9qutC2Uk9PVA',
            'id': '1kt6SGM89ixO325jHI6E5PLeIHQRu-0P0'
        }]
    })
    f.SetContentFile(location)
    f.Upload(param={'supportsTeamDrives': True})
    return f['embedLink']


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
            filename = request.FILES['file'].name
            filename = key + '.' + list(map(str, filename.split('.')))[-1]
            location = os.path.join(str(settings.BASE_DIR), 'tmp')
            location = os.path.join(location, filename)
            file = request.FILES['file'].read()
            with open(location, 'wb') as temp_file:
                temp_file.write(file)
            embedLink = upload(filename, location)
            os.remove(location)
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
