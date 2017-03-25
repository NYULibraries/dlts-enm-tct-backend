from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.UpdateRelationView.as_view()),
    url(r'^new-default/$', views.CreateDefaultRelatedBasketView.as_view()),
    url(r'^new/$', views.CreateFullRelatedBasketView.as_view()),
    url(r'^bulk-delete/$', views.BulkRelationDeleteView.as_view()),
    url(r'^forbidden/(?P<basket_id>\d+)/$', views.ForbiddenRelationsByBasketView.as_view()),
    url(r'^rtype/all/$', views.RelationTypesAllView.as_view()),
    url(r'^rtype/new/$', views.RelationTypeCreateView.as_view()),
    url(r'^rtype/with-counts/$', views.RelationTypeWithCountsView.as_view()),
    url(r'^rtype/(?P<pk>\d+)/$', views.RelationTypeUpdateView.as_view())
]
