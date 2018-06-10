from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    url(r'', include('kriisis_page.api_urls')),
    path('admin/', admin.site.urls),
    url(r'', include('frontend.urls'))
]
