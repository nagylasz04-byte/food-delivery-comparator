from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import EtteremEtelInfo, Mentes  # <--- FONTOS: Mentes is kell!


# ---------- ÉTTEREM–ÉTEL INFÓ (ajánlatok) ----------
class InfoListView(ListView):
    """
    Ajánlatok listája. ?etel=<id> esetén az adott étel ajánlatai.
    """
    model = EtteremEtelInfo
    template_name = "compare/info_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("etel", "etterem")
        etel_id = self.request.GET.get("etel")
        if etel_id:
            qs = qs.filter(etel_id=etel_id)
        return qs.order_by("ar")


class InfoDetailView(DetailView):
    model = EtteremEtelInfo
    template_name = "compare/info_detail.html"


class InfoCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = EtteremEtelInfo
    fields = ["etel", "etterem", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.add_etteremetelinfo"
    template_name = "compare/info_form.html"
    success_url = reverse_lazy("compare:info_list")


class InfoUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = EtteremEtelInfo
    fields = ["etel", "etterem", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.change_etteremetelinfo"
    template_name = "compare/info_form.html"
    success_url = reverse_lazy("compare:info_list")


class InfoDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = EtteremEtelInfo
    permission_required = "compare.delete_etteremetelinfo"
    template_name = "compare/confirm_delete.html"
    success_url = reverse_lazy("compare:info_list")


# ---------- MENTÉS (kedvencek / elmentett tételek) ----------
class MentesListView(ListView):
    model = Mentes
    template_name = "compare/mentes_list.html"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("felh", "etel")
        # ha csak saját mentéseket akarsz mutatni bejelentkezett felhasználónak:
        # if self.request.user.is_authenticated:
        #     qs = qs.filter(felh=self.request.user)
        return qs.order_by("-id")


class MentesDetailView(DetailView):
    model = Mentes
    template_name = "compare/mentes_detail.html"


class MentesCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Mentes
    fields = ["felh", "etel"]
    permission_required = "compare.add_mentes"
    template_name = "compare/mentes_form.html"
    success_url = reverse_lazy("compare:mentes_list")


class MentesUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Mentes
    fields = ["felh", "etel"]
    permission_required = "compare.change_mentes"
    template_name = "compare/mentes_form.html"
    success_url = reverse_lazy("compare:mentes_list")


class MentesDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Mentes
    permission_required = "compare.delete_mentes"
    template_name = "compare/confirm_delete.html"
    success_url = reverse_lazy("compare:mentes_list")
