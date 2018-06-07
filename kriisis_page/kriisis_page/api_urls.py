from django.conf.urls import url, include

includes = [
    url(r'', include('accounts.api_urls')),
]

urlpatterns = [
    url(r'^api/v1/', include(includes)),
]
