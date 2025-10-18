from django.contrib import admin
from django.urls import path, include
from foodcompare.views import SiteIndexView

urlpatterns = [
    # Home page (site index)
    path("", SiteIndexView.as_view(), name="home"),

    # Admin + appok
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("", include("billing.urls")),
    path("", include("compare.urls")),
    path("", include("users.urls")),
]
