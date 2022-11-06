from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


handler404 = 'core.views.page_not_found_404'
handler403 = 'core.views.csrf_failure_403'
handler500 = 'core.views.internal_server_error_500'

urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('accounts/', include('users.urls', namespace='users_1')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
