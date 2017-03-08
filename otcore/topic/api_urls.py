from django.conf.urls import url

from .views import AllTypesView, RemoveTypeView, AllTypesWithCountsView


urlpatterns = [
    url(r'^ttype/all/$', AllTypesView.as_view(), name='api-ttype-all'),
    url(r'^ttype/new/$', AllTypesView.as_view(), name='api-ttype-new'),
    url(r'^ttype/withCounts/$', AllTypesWithCountsView.as_view(), name='api-ttype-all-with-counts'),
    url(r'^ttype/(?P<pk>\d+)/$', RemoveTypeView.as_view(), name='api-ttype-remove'),
]
