from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Q, Min, Count, Avg, F, Value, DecimalField, Case, When, Subquery, OuterRef, Sum, Prefetch
from django.db.models.functions import Coalesce

from foodcompare.mixins import LoginRequired, WritePermissionRequired, StaffRequired
from .models import Etterem, Etel
from compare.models import Mentes


# ---------- ÉTTEREM: teljes CRUD ----------
class EtteremListView(StaffRequired, ListView):
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
class EtelListView(StaffRequired, ListView):
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
    paginate_by = 5
    context_object_name = "talalatok"

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        sort = self.request.GET.get("sort", "alap")

        # VISSZAIRÁNYÚ KAPCSOLAT NEVE AZ ÉTEL -> EtteremEtelInfo FELÉ:
        REL = "etterem_info"

        # Compute per-etel the minimal "visible" offer price (ar + cost_sum)
        # Use Subquery on EtteremEtelInfo filtered by etel=OuterRef('pk') and
        # annotate each offer with restaurant/platform cost sums similar to
        # the product page logic, then select the smallest total_price.
        from compare.models import EtteremEtelInfo  # local import to build subquery

        from billing.models import EtteremKoltseg

        offers_subq = (
            EtteremEtelInfo.objects
            .filter(etel=OuterRef('pk'))
            .annotate(
                _rest_sum=Coalesce(
                    Subquery(
                        EtteremKoltseg.objects
                        .filter(etterem=OuterRef('etterem_id'))
                        .values('etterem')
                        .annotate(s=Sum('osszeg'))
                        .values('s')
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                _plat_sum=Coalesce(
                    Subquery(
                        EtteremKoltseg.objects
                        .filter(etterem__isnull=True, platform=OuterRef('platform'))
                        .values('platform')
                        .annotate(s=Sum('osszeg'))
                        .values('s')
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .annotate(
                cost_sum=Case(
                    When(_plat_sum__gt=0, then=F('_plat_sum')),
                    default=F('_rest_sum'),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            .annotate(total_price=F('ar') + F('cost_sum'))
            .order_by('total_price')
            .values('total_price')[:1]
        )

        base = (
            Etel.objects.all()
            .annotate(
                min_total_price=Subquery(offers_subq, output_field=DecimalField(max_digits=10, decimal_places=2)),
                offer_count=Count(f"{REL}", distinct=True),
                avg_rating=Avg(f"{REL}__felhaszn_ertekelesek"),
            )
            .prefetch_related(
                Prefetch(
                    'etterem_info',
                    queryset=EtteremEtelInfo.objects.select_related('etterem')
                )
            )
        )

        if q:
            base = base.filter(
                Q(nev__icontains=q)
                | Q(leiras__icontains=q)
                | Q(kategoria__icontains=q)
            )

        # City filter
        city = self.request.GET.get("city", "").strip()
        if city:
            base = base.filter(
                etterem_info__etterem__cim__icontains=city
            ).distinct()

        ordering = {
            "alap": ("nev",),
            "olcso": ("min_total_price", "nev"),
            "draga": ("-min_total_price", "nev"),
            "ertekeles": ("-avg_rating", "nev"),
            "nev": ("nev",),
        }.get(sort, ("nev",))

        return base.order_by(*ordering)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["sort"] = self.request.GET.get("sort", "alap")
        ctx["city"] = self.request.GET.get("city", "").strip()
        
        # Collect all unique cities from available restaurants
        from catalog.models import Etterem
        cities = set()
        for etterem in Etterem.objects.exclude(cim="").exclude(cim__isnull=True):
            c = etterem.get_city()
            if c:
                cities.add(c)
        ctx["available_cities"] = sorted(cities)
        
        # saved etel ids for the current user (to render save/unsave buttons)
        if self.request.user.is_authenticated:
            ctx["saved_etel_ids"] = set(Mentes.objects.filter(felhasznalo=self.request.user).values_list("etel_id", flat=True))
        else:
            ctx["saved_etel_ids"] = set()
        return ctx
