from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^document/(?P<pk>\d+)/$', views.EpubDocumentDetailView.as_view()),
    url(r'^document/all/$', views.EpubDocumentListView.as_view()),
    url(r'^location/(?P<pk>\d+)/$', views.EpubLocationView.as_view()),
    url(r'^index/(?P<location_id>\d+)/$', views.IndexURLView.as_view()),
    url(r'^index-pattern/all/$', views.AllIndexPatternsView.as_view()),
    url(r'automatic-relations/(?P<basket_id>\d+)/$', views.AutomaticRelationView.as_view()),
]
