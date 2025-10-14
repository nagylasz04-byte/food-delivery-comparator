from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

    # Admin + appok
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("", include("billing.urls")),
    path("", include("compare.urls")),
]
