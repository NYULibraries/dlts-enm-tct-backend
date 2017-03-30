from django.conf.urls import url 

from . import views

urlpatterns = [
    url(r'^upload/$', views.ProcessReconciliationView.as_view()),
]
