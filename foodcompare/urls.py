from django.contrib import admin
from django.urls import path, include
from django.urls import reverse_lazy
from foodcompare.views import SiteIndexView, simple_logout

urlpatterns = [
    # Home page (site index)
    path("", SiteIndexView.as_view(), name="home"),

    # Logout (frontend logout redirecting to home)
    path("logout/", simple_logout, name="logout"),

    # Admin + appok
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("", include("billing.urls")),
    path("", include("compare.urls")),
    path("", include("users.urls")),
]
