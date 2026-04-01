from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

admin.site.site_header = "Marketplace Admin"
admin.site.site_title = "Marketplace"
admin.site.index_title = "Dashboard"


def root(_request):
    return JsonResponse(
        {"status": "ok", "message": "MarketPy Django API scaffold is running"}
    )


urlpatterns = [
    path("", root, name="root"),
    path("", include("accounts.urls")),
    path("", include("catalog.urls")),
    path("", include("orders.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG and settings.MEDIA_STORAGE_BACKEND == "filesystem":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
