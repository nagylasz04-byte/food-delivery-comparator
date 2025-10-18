from django.contrib import admin
from django.urls import path, include
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from foodcompare.views import SiteIndexView, simple_logout

urlpatterns = [
    # Home page (site index)
    path("", SiteIndexView.as_view(), name="home"),

    # Logout (frontend logout redirecting to home)
    path("logout/", simple_logout, name="logout"),
    # Frontend login for non-admin users
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login"),

    # Admin + appok
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("", include("billing.urls")),
    path("", include("compare.urls")),
    path("", include("users.urls")),
]
