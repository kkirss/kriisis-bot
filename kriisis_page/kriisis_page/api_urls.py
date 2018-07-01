from django.conf.urls import url, include

includes = [
    url(r'', include('accounts.api_urls')),
    url(r'', include('scraper.api_urls')),
]

urlpatterns = [
    url(r'^v1/', include(includes)),
]
