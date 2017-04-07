from django.conf.urls import url

from .views import AddWeblinkView, SingleWeblinkView, ListWeblinkView

urlpatterns = [
    url(r'^new/$', AddWeblinkView.as_view(), name='api-weblink-add'),
    url(r'^(?P<pk>\d+)/$', SingleWeblinkView.as_view(), name='api-weblink-remove'),
    url(r'^list/$', ListWeblinkView.as_view(), name='api-weblink-list'),
]
