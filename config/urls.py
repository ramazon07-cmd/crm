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

# Router
router = DefaultRouter()
router.register("users",    UserViewSet,    basename="user")
router.register("students", StudentViewSet, basename="student")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("teachers", TeacherViewSet, basename="teacher")

# ✅ TO'LIQ SWAGGER KONFIGURATSIYA
schema = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version="v1",
        description="""
## CRM Tizimi REST API

### Autentifikatsiya
Barcha himoyalangan endpointlar uchun Token kerak:
Authorization: Token <your_token_here>

### Endpointlar
- **Users** — Ro'yxatdan o'tish, login, profil boshqarish
- **Students** — Talabalar CRUD
- **Teachers** — O'qituvchilar CRUD  
- **Subjects** — Fanlar CRUD
        """,
        terms_of_service="https://crm.uz/terms/",
        contact=openapi.Contact(
            name="CRM Support",
            email="admin@crm.uz",
            url="https://crm.uz/support"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("swagger/", schema.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/",   schema.with_ui("redoc",   cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema.without_ui(cache_timeout=0), name="schema-json"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)