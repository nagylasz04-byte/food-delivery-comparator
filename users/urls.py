from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("felhasznalo/", views.FelhasznaloListView.as_view(), name="felhasznalo_list"),
    path("felhasznalo/<int:pk>/", views.FelhasznaloDetailView.as_view(), name="felhasznalo_detail"),
    path("felhasznalo/uj/", views.FelhasznaloCreateView.as_view(), name="felhasznalo_create"),
    path("felhasznalo/<int:pk>/szerkesztes/", views.FelhasznaloUpdateView.as_view(), name="felhasznalo_update"),
    path("felhasznalo/<int:pk>/torles/", views.FelhasznaloDeleteView.as_view(), name="felhasznalo_delete"),
    # Jog and FelhJog routes removed (models deleted)
]

# Public registration URL (friendly path)
urlpatterns += [
    path("register/", views.RegisterView.as_view(), name="register"),
]
