"""
Root URL configuration for CongthongtintuyensinhDUE project.
Strictly acts as top-level router without hosting views directly.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin site
    path('admin/', admin.site.urls),

    # University Portal app (Faculties, Youth Union, Clubs, Student Life, Enrollment Guide)
    path('', include('portal.urls')),

    # Admissions app primary namespace
    path('', include('admissions.urls', namespace='admissions')),

    # Backward compatibility namespace for templates referencing {% url 'tuyensinh:...' %}
    path('', include('admissions.urls', namespace='tuyensinh')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
