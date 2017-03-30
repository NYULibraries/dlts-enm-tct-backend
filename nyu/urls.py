"""
nyu URL Configuration
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from nyu.admin import nyu_admin

from django.conf import settings

urlpatterns = [
    url(r'^admin/', include(nyu_admin.urls)),
    url(r'^api/review/', include('otx_review.api_urls')),
    url(r'^api/epub/', include('manuscripts.api_urls')),
    url(r'^api/reconciliation/', include('reconciliation.api_urls')),
    url(r'^api/weblink/', include('otx_weblink.api_urls')),
    url(r'^api/', include('otcore.api_urls')),
    url(r'^rest-auth/', include('rest_auth.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
