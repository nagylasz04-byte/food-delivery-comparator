from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce

from catalog.models import Etel
from .models import EtteremEtelInfo
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
        offers = (
            EtteremEtelInfo.objects
            .filter(etel_id=etel_id)
            .select_related("etterem", "etel")
            .annotate(
                cost_sum=Coalesce(
                    Sum("etterem__koltsegek__osszeg"),
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            .annotate(total_price=F("ar") + F("cost_sum"))
            .order_by("total_price", "ar")
        )

        min_total = offers.first().total_price if offers else None
        offer_count = offers.count()

        # költségek listázása éttermenként
        koltsegek_by_etterem = {}
        if offer_count:
            etterem_ids = [o.etterem_id for o in offers]
            for k in EtteremKoltseg.objects.filter(etterem_id__in=etterem_ids):
                koltsegek_by_etterem.setdefault(k.etterem_id, []).append(k)

        ctx.update({
            "etel": etel,
            "offers": offers,
            "min_total": min_total,
            "offer_count": offer_count,
            "koltsegek_by_etterem": koltsegek_by_etterem,
        })
        return ctx


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
