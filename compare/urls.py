from django.urls import path
from . import views

app_name = "compare"

urlpatterns = [
    path("info/", views.InfoListView.as_view(), name="info_list"),
    path("info/uj/", views.InfoCreateView.as_view(), name="info_create"),
    path("info/<int:pk>/", views.InfoDetailView.as_view(), name="info_detail"),
    path("info/<int:pk>/szerkeszt/", views.InfoUpdateView.as_view(), name="info_update"),
    path("info/<int:pk>/torles/", views.InfoDeleteView.as_view(), name="info_delete"),

    path("mentes/", views.MentesListView.as_view(), name="mentes_list"),
    path("mentes/uj/", views.MentesCreateView.as_view(), name="mentes_create"),
    path("mentes/<int:pk>/", views.MentesDetailView.as_view(), name="mentes_detail"),
    path("mentes/<int:pk>/szerkeszt/", views.MentesUpdateView.as_view(), name="mentes_update"),
    path("mentes/<int:pk>/torles/", views.MentesDeleteView.as_view(), name="mentes_delete"),
]
