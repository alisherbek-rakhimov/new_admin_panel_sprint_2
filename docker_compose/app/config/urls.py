from django.contrib import admin
from django.urls import include, path
from .settings import DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.api.urls')),
]

if DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('debug/', include(debug_toolbar.urls)),
        *urlpatterns
    ]
