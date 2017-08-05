from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^document/all/$', views.DocumentListView.as_view()),
    url(r'^document/(?P<pk>\d+)/$', views.DocumentDetailView.as_view()),
    url(r'^location/(?P<pk>\d+)/$', views.LocationDetailView.as_view()),
    url(r'^occurrence/(?P<pk>\d+)/$', views.OccurrenceAlterView.as_view()),
    url(r'^occurrence/new/$', views.OccurrenceNewView.as_view()),
    url(r'^occurrence/newWithHit/$', views.OccurrenceNewWithHitView.as_view()),
    url(r'^occurrence/newOnBasket/$', views.OccurrenceNewOnBasketView.as_view()),
    url(r'^occurrence/newFromUISelect/$', views.OccurrenceFromUISelectView.as_view()),
]
