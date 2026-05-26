from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static

from users.views import UserViewSet
from students.views import StudentViewSet
from subjects.views import SubjectViewSet
from teachers.views import TeacherViewSet

#  Router
router = DefaultRouter()
router.register("users",    UserViewSet,    basename="user")
router.register("students", StudentViewSet, basename="student")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("teachers", TeacherViewSet, basename="teacher")

#  Swagger / OpenAPI
schema = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version="v1",
        description="CRM tizimi uchun REST API dokumentatsiyasi",
        contact=openapi.Contact(email="admin@crm.uz"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

#  URL Patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    # Swagger UI
    path("swagger/", schema.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/",   schema.with_ui("redoc",   cache_timeout=0), name="schema-redoc"),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)