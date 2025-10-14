# catalog/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import Etterem, Etel


# ========================
#     ÉTTEREM (CRUD)
# ========================

class EtteremListView(ListView):
    """Éttermek listázása (bárki láthatja)."""
    model = Etterem
    template_name = "catalog/etterem_list.html"
    paginate_by = 20
    ordering = ["nev"]


class EtteremDetailView(DetailView):
    """Egy étterem részletes adatai (bárki láthatja)."""
    model = Etterem
    template_name = "catalog/etterem_detail.html"


class EtteremCreateView(LoginRequired, WritePermissionRequired, CreateView):
    """Új étterem létrehozása (csak staff/admin)."""
    model = Etterem
    fields = ["nev", "cim", "platform"]
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")


class EtteremUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    """Étterem módosítása (csak staff/admin)."""
    model = Etterem
    fields = ["nev", "cim", "platform"]
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")


class EtteremDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    """Étterem törlése (csak staff/admin)."""
    model = Etterem
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:etterem_list")


# ========================
#     ÉTEL (READ-ONLY)
# ========================

class EtelListView(ListView):
    """Ételek listázása (read-only, bárki láthatja)."""
    model = Etel
    template_name = "catalog/etel_list.html"
    paginate_by = 20
    ordering = ["nev"]


class EtelDetailView(DetailView):
    """Egy étel részletes adatai (read-only, bárki láthatja)."""
    model = Etel
    template_name = "catalog/etel_detail.html"
