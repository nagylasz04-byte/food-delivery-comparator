from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Étterem
    path("etterem/", views.EtteremListView.as_view(), name="etterem_list"),
    path("etterem/uj/", views.EtteremCreateView.as_view(), name="etterem_create"),
    path("etterem/<int:pk>/", views.EtteremDetailView.as_view(), name="etterem_detail"),
    path("etterem/<int:pk>/szerkeszt/", views.EtteremUpdateView.as_view(), name="etterem_update"),
    path("etterem/<int:pk>/torles/", views.EtteremDeleteView.as_view(), name="etterem_delete"),

    # Étel
    path("etel/", views.EtelListView.as_view(), name="etel_list"),
    path("etel/uj/", views.EtelCreateView.as_view(), name="etel_create"),
    path("etel/<int:pk>/", views.EtelDetailView.as_view(), name="etel_detail"),
    path("etel/<int:pk>/szerkeszt/", views.EtelUpdateView.as_view(), name="etel_update"),
    path("etel/<int:pk>/torles/", views.EtelDeleteView.as_view(), name="etel_delete"),
]
