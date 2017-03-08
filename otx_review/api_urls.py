from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<basket_id>\d+)/$', views.SetReviewed.as_view()),
    url(r'^baskets/all/$', views.ReviewAllBasketsView.as_view()),
    url(r'^baskets/search/$', views.ReviewBasketSearchView.as_view()),
    url(r'^hits/all/$', views.ReviewAllHitsView.as_view()),
    url(r'^hits/search/$', views.ReviewHitSearchView.as_view()),
    url(r'^reports/all/$', views.AllReportsView.as_view()),
    url(r'^reports/(?P<pk>\d+)/$', views.DeleteReportView.as_view()),
    url(r'^reports/new/$', views.NewReportView.as_view()),
    url(r'^reports/types/$', views.AllReportTypesView.as_view()),
]
