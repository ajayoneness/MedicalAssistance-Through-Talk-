
from django.urls import path
from . import views


urlpatterns = [
    path('',views.index, name="index"),
    path('dashboard/',views.dashboard, name="dashboard"),
    path('save_recording/', views.save_recording, name='save_recording'),
    path('convert/', views.convert, name='convert'),
    path('patientlist/', views.patientlist, name='patientlist'),
    path('patientprofile/<int:idd>', views.patientprofile, name='patientprofile'),

]
