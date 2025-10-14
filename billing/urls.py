from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("koltseg/", views.KoltsegListView.as_view(), name="koltseg_list"),
    path("koltseg/uj/", views.KoltsegCreateView.as_view(), name="koltseg_create"),
    path("koltseg/<int:pk>/", views.KoltsegDetailView.as_view(), name="koltseg_detail"),
    path("koltseg/<int:pk>/szerkeszt/", views.KoltsegUpdateView.as_view(), name="koltseg_update"),
    path("koltseg/<int:pk>/torles/", views.KoltsegDeleteView.as_view(), name="koltseg_delete"),
]
