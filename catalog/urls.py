from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("etterem/", views.EtteremListView.as_view(), name="etterem_list"),
    path("etterem/<int:pk>/", views.EtteremDetailView.as_view(), name="etterem_detail"),
    path("etterem/uj/", views.EtteremCreateView.as_view(), name="etterem_create"),
    path("etterem/<int:pk>/szerkeszt/", views.EtteremUpdateView.as_view(), name="etterem_update"),
    path("etterem/<int:pk>/torles/", views.EtteremDeleteView.as_view(), name="etterem_delete"),

    path("etel/", views.EtelListView.as_view(), name="etel_list"),
    path("etel/<int:pk>/", views.EtelDetailView.as_view(), name="etel_detail"),
]
