from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Q, Min, Count, Avg

from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import Etterem, Etel


# ---------- ÉTTEREM: teljes CRUD ----------
class EtteremListView(ListView):
    model = Etterem
    template_name = "catalog/etterem_list.html"


class EtteremDetailView(DetailView):
    model = Etterem
    template_name = "catalog/etterem_detail.html"


class EtteremCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Etterem
    fields = ["nev", "cim", "platform"]
    permission_required = "catalog.add_etterem"
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")


class EtteremUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Etterem
    fields = ["nev", "cim", "platform"]
    permission_required = "catalog.change_etterem"
    template_name = "catalog/etterem_form.html"
    success_url = reverse_lazy("catalog:etterem_list")


class EtteremDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Etterem
    permission_required = "catalog.delete_etterem"
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:etterem_list")


# ---------- ÉTEL: lista + részlet + (staff) CRUD ----------
class EtelListView(ListView):
    model = Etel
    paginate_by = 20
    template_name = "catalog/etel_list.html"


class EtelDetailView(DetailView):
    model = Etel
    template_name = "catalog/etel_detail.html"


class EtelCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = Etel
    fields = ["nev", "leiras", "kategoria", "kep_url"]
    permission_required = "catalog.add_etel"
    template_name = "catalog/etel_form.html"
    success_url = reverse_lazy("catalog:etel_list")


class EtelUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = Etel
    fields = ["nev", "leiras", "kategoria", "kep_url"]
    permission_required = "catalog.change_etel"
    template_name = "catalog/etel_form.html"
    success_url = reverse_lazy("catalog:etel_list")


class EtelDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = Etel
    permission_required = "catalog.delete_etel"
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:etel_list")


# ---------- KERESÉS / RENDEZÉS (ár-információkkal) ----------
class EtelSearchView(ListView):
    template_name = "catalog/kereses.html"
    paginate_by = 20
    context_object_name = "talalatok"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort", "alap")

        # VISSZAIRÁNYÚ KAPCSOLAT NEVE AZ ÉTEL -> EtteremEtelInfo FELÉ:
        # a te sémádban ez 'etterem_info' (ezt írja a hibaüzenet is)
        REL = "etterem_info"

        base = (
            Etel.objects.all()
            .annotate(
                min_price=Min(f"{REL}__ar"),
                offer_count=Count(f"{REL}", distinct=True),
                avg_rating=Avg(f"{REL}__felhaszn_ertekelesek"),
            )
        )

        if q:
            base = base.filter(
                Q(nev__icontains=q)
                | Q(leiras__icontains=q)
                | Q(kategoria__icontains=q)
            )

        ordering = {
            "alap": ("nev",),
            "olcso": ("min_price", "nev"),
            "draga": ("-min_price", "nev"),
            "ertekeles": ("-avg_rating", "nev"),
            "nev": ("nev",),
        }.get(sort, ("nev",))

        return base.order_by(*ordering)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["sort"] = self.request.GET.get("sort", "alap")
        return ctx
