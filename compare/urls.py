from django.urls import path
from . import views

app_name = "compare"

urlpatterns = [
    # ÚJ termékoldal (ár-összevetés oldal):
    path("termek/<int:etel_id>/", views.OffersForEtelView.as_view(), name="offers_for_etel"),

    # MEGLÉVŐ útvonalak (maradnak)
    path("info/", views.InfoListView.as_view(), name="info_list"),
    path("info/<int:pk>/", views.InfoDetailView.as_view(), name="info_detail"),
    path("info/uj/", views.InfoCreateView.as_view(), name="info_create"),
    path("info/<int:pk>/szerkesztes/", views.InfoUpdateView.as_view(), name="info_update"),
    path("info/<int:pk>/torles/", views.InfoDeleteView.as_view(), name="info_delete"),
]
