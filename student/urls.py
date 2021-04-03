from django.urls import path

from . import views

urlpatterns = [
    path('logout/', views.logoutUser, name='logout'),
    path('', views.getCourses, name='studentindex'),
    path('enroll/', views.enrollInCourse, name='enroll'),
    path('submissions/', views.getSubmissions, name='submissions'),
    path('course/<str:courseid>/', views.getCourseDetail, name='studentcourse'),
    path('course/<str:courseid>/lesson/<str:lessonid>', views.getLessonDetail, name='studentlesson'),
    path('course/<str:courseid>/assignment/<str:assignmentid>', views.getAssignmentDetail, name='assignment'),
]
