from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import Etterem, Etel

# -------- Étterem (CRUD) --------
class EtteremListView(ListView):
    model = Etterem
    template_name = "catalog/etterem_list.html"
    paginate_by = 20
    ordering = ["nev"]

class EtteremDetailView(DetailView):
    model = Etterem
    template_name = "catalog/etterem_detail.html"

class EtteremCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Etterem
    fields = ["nev", "cim", "platform"]
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")

class EtteremUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Etterem
    fields = ["nev", "cim", "platform"]
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")

class EtteremDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Etterem
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:etterem_list")

# -------- Étel (READ + admin CRUD) --------
class EtelListView(ListView):
    model = Etel
    template_name = "catalog/etel_list.html"
    paginate_by = 20
    ordering = ["nev"]

class EtelDetailView(DetailView):
    model = Etel
    template_name = "catalog/etel_detail.html"

class EtelCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Etel
    fields = ["nev", "leiras", "kategoria", "kep_url"]
    template_name = "catalog/etel_form.html"
    success_url = reverse_lazy("catalog:etel_list")

class EtelUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Etel
    fields = ["nev", "leiras", "kategoria", "kep_url"]
    template_name = "catalog/etel_form.html"
    success_url = reverse_lazy("catalog:etel_list")

class EtelDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Etel
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:etel_list")
