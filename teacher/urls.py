from django.urls import path

from . import views

urlpatterns = [
    path('logout/', views.logoutUser, name='logout'),
    path('', views.getCourses, name='index'),
    path('create/', views.createCourse, name='create'),
    path('course/<str:courseid>/', views.getCourseDetail, name='course'),
    path('course/<str:courseid>/lesson/<str:lessonid>', views.getLessonDetail, name='lesson'),
    path('course/<str:courseid>/add/lesson/', views.addLesson, name='addlesson'),
    path('course/<str:courseid>/assignment/<str:assignmentid>', views.getAssignmentDetail, name='assignment'),
    path('course/<str:courseid>/add/assignment/', views.addAssignment, name='addassignment'),
    path('course/<str:courseid>/students', views.getStudentDetail, name='student'),
]
