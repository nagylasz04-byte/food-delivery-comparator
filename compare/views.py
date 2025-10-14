from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import EtteremEtelInfo, Mentes

# ----- Etterem–Etel info (CRUD)
class InfoListView(ListView):
    model = EtteremEtelInfo
    paginate_by = 20
    template_name = "compare/info_list.html"

class InfoDetailView(DetailView):
    model = EtteremEtelInfo
    template_name = "compare/info_detail.html"

class InfoCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = EtteremEtelInfo
    fields = ["etel", "etterem", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.add_etteremetelinfo"
    success_url = reverse_lazy("compare:info_list")
    template_name = "compare/info_form.html"

class InfoUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = EtteremEtelInfo
    fields = ["etel", "etterem", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.change_etteremetelinfo"
    success_url = reverse_lazy("compare:info_list")
    template_name = "compare/info_form.html"

class InfoDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = EtteremEtelInfo
    permission_required = "compare.delete_etteremetelinfo"
    success_url = reverse_lazy("compare:info_list")
    template_name = "compare/confirm_delete.html"

# ----- Mentés (CRUD)
class MentesListView(ListView):
    model = Mentes
    paginate_by = 20
    template_name = "compare/mentes_list.html"

class MentesDetailView(DetailView):
    model = Mentes
    template_name = "compare/mentes_detail.html"

class MentesCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Mentes
    fields = ["felhasznalo", "etel"]
    permission_required = "compare.add_mentes"
    success_url = reverse_lazy("compare:mentes_list")
    template_name = "compare/mentes_form.html"

class MentesUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Mentes
    fields = ["felhasznalo", "etel"]
    permission_required = "compare.change_mentes"
    success_url = reverse_lazy("compare:mentes_list")
    template_name = "compare/mentes_form.html"

class MentesDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Mentes
    permission_required = "compare.delete_mentes"
    success_url = reverse_lazy("compare:mentes_list")
    template_name = "compare/confirm_delete.html"
