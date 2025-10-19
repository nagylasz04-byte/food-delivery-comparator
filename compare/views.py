from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.db.models import Sum, F, Value, DecimalField, Avg, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from catalog.models import Etel
from .models import EtteremEtelInfo, Mentes
from billing.models import EtteremKoltseg

# ha már van nálad ez a mixin, maradhat
try:
    from foodcompare.mixins import LoginRequired, WritePermissionRequired
except Exception:  # fejlesztői kényelemre
    class LoginRequired: ...
    class WritePermissionRequired: ...


class OffersForEtelView(TemplateView):
    """
    KÜLÖN TERMÉKOLDAL: egy adott étel összes platform/étterem ajánlata.
    URL: /termek/<etel_id>/
    """
    template_name = "compare/offers_for_etel.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        etel_id = self.kwargs["etel_id"]
        etel = get_object_or_404(Etel, pk=etel_id)

        # ajánlatok + összesített költség + total ár
        # Sum hidden costs attached to the specific restaurant PLUS
        # platform-level costs (EtteremKoltseg rows where etterem is null and platform matches)
        # We use Subquery to aggregate each side and add them together per-offer.
        restaurant_sum_subq = (
            EtteremKoltseg.objects
            .filter(etterem=OuterRef('etterem_id'))
            .values('etterem')
            .annotate(s=Sum('osszeg'))
            .values('s')
        )
        # NOTE: match platform-level costs to the offer's restaurant platform
        # OuterRef must point to the offer's etterem__platform
        platform_sum_subq = (
            EtteremKoltseg.objects
            .filter(platform=OuterRef('etterem__platform'), etterem__isnull=True)
            .values('platform')
            .annotate(s=Sum('osszeg'))
            .values('s')
        )

        offers = (
            EtteremEtelInfo.objects
            .filter(etel_id=etel_id)
            .select_related("etterem", "etel")
            .annotate(
                _rest_sum=Coalesce(
                    Subquery(restaurant_sum_subq, output_field=DecimalField(max_digits=10, decimal_places=2)),
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                _plat_sum=Coalesce(
                    Subquery(platform_sum_subq, output_field=DecimalField(max_digits=10, decimal_places=2)),
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .annotate(cost_sum=F('_rest_sum') + F('_plat_sum'))
            .annotate(total_price=F("ar") + F("cost_sum"))
            .order_by("total_price", "ar")
        )

        min_total = offers.first().total_price if offers else None
        offer_count = offers.count()
        avg_rating = (
            EtteremEtelInfo.objects.filter(etel_id=etel_id)
            .aggregate(r=Avg("felhaszn_ertekelesek"))
            .get("r")
        )

        # költségek listázása éttermenként
        koltsegek_by_etterem = {}
        if offer_count:
            etterem_ids = [o.etterem_id for o in offers]
            for k in EtteremKoltseg.objects.filter(etterem_id__in=etterem_ids):
                koltsegek_by_etterem.setdefault(k.etterem_id, []).append(k)

        # platform-level costs (etterem is null) grouped by platform
        koltsegek_by_platform = {}
        if offer_count:
            # collect the platform value from each offer's restaurant (etterem.platform)
            platforms = [o.etterem.platform for o in offers if o.etterem]
            for k in EtteremKoltseg.objects.filter(etterem__isnull=True, platform__in=platforms):
                koltsegek_by_platform.setdefault(k.platform, []).append(k)

        ctx.update({
            "etel": etel,
            "offers": offers,
            "min_total": min_total,
            "offer_count": offer_count,
            "avg_rating": avg_rating,
            "koltsegek_by_etterem": koltsegek_by_etterem,
            "koltsegek_by_platform": koltsegek_by_platform,
            "is_saved": (
                self.request.user.is_authenticated and
                Mentes.objects.filter(felhasznalo=self.request.user, etel=etel).exists()
            ),
        })
        return ctx


@login_required
def toggle_save(request, etel_id: int):
    """Create or delete a Mentes for the current user and redirect back to the offers page."""
    etel = get_object_or_404(Etel, pk=etel_id)
    existing = Mentes.objects.filter(felhasznalo=request.user, etel=etel)
    if existing.exists():
        existing.delete()
    else:
        Mentes.objects.create(felhasznalo=request.user, etel=etel)
    return redirect("compare:offers_for_etel", etel_id=etel.id)


@method_decorator(login_required, name="dispatch")
class SavedFoodsView(ListView):
    template_name = "compare/saved_foods.html"
    context_object_name = "saved"

    def get_queryset(self):
        qs = Mentes.objects.select_related("etel")
        if self.request.user.is_staff:
            return qs.order_by("-letrehozva")
        return qs.filter(felhasznalo=self.request.user).order_by("-letrehozva")


# ---- (a korábbi CRUD/Lista nézeteid maradhatnak változatlanul) ----
class InfoListView(ListView):
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
    fields = ["etel", "etterem", "platform", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.add_etteremetelinfo"
    template_name = "compare/info_form.html"
    success_url = reverse_lazy("compare:info_list")


class InfoUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = EtteremEtelInfo
    fields = ["etel", "etterem", "platform", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio"]
    permission_required = "compare.change_etteremetelinfo"
    template_name = "compare/info_form.html"
    success_url = reverse_lazy("compare:info_list")


class InfoDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = EtteremEtelInfo
    permission_required = "compare.delete_etteremetelinfo"
    template_name = "compare/confirm_delete.html"
    success_url = reverse_lazy("compare:info_list")
