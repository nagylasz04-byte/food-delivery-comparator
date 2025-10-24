from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("felhasznalo/", views.FelhasznaloListView.as_view(), name="felhasznalo_list"),
    path("felhasznalo/<int:pk>/", views.FelhasznaloDetailView.as_view(), name="felhasznalo_detail"),
    path("felhasznalo/uj/", views.FelhasznaloCreateView.as_view(), name="felhasznalo_create"),
    path("felhasznalo/<int:pk>/szerkesztes/", views.FelhasznaloUpdateView.as_view(), name="felhasznalo_update"),
    path("felhasznalo/<int:pk>/torles/", views.FelhasznaloDeleteView.as_view(), name="felhasznalo_delete"),

    path("jog/", views.JogListView.as_view(), name="jog_list"),
    path("jog/uj/", views.JogCreateView.as_view(), name="jog_create"),
    path("jog/<int:pk>/", views.JogDetailView.as_view(), name="jog_detail"),
    path("jog/<int:pk>/szerkesztes/", views.JogUpdateView.as_view(), name="jog_update"),
    path("jog/<int:pk>/torles/", views.JogDeleteView.as_view(), name="jog_delete"),

    path("felhjog/", views.FelhJogListView.as_view(), name="felhjog_list"),
    path("felhjog/uj/", views.FelhJogCreateView.as_view(), name="felhjog_create"),
    path("felhjog/<int:pk>/", views.FelhJogDetailView.as_view(), name="felhjog_detail"),
    path("felhjog/<int:pk>/szerkesztes/", views.FelhJogUpdateView.as_view(), name="felhjog_update"),
    path("felhjog/<int:pk>/torles/", views.FelhJogDeleteView.as_view(), name="felhjog_delete"),
]

# Public registration URL (friendly path)
urlpatterns += [
    path("register/", views.RegisterView.as_view(), name="register"),
]
