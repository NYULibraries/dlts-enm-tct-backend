from django.conf.urls import url, include

urlpatterns = [
    url(r'^hit/', include('otcore.hit.api_urls')),
    url(r'^relation/', include('otcore.relation.api_urls')),
    url(r'^topic/', include('otcore.topic.api_urls')),
    url(r'^occurrence/', include('otcore.occurrence.api_urls')),
]
