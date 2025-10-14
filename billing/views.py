from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from foodcompare.mixins import LoginRequired, WritePermissionRequired
from .models import EtteremKoltseg

class KoltsegListView(ListView):
    model = EtteremKoltseg
    paginate_by = 20
    template_name = "billing/koltseg_list.html"

class KoltsegDetailView(DetailView):
    model = EtteremKoltseg
    template_name = "billing/koltseg_detail.html"

class KoltsegCreateView(LoginRequired, WritePermissionRequired, CreateView):
    model = EtteremKoltseg
    fields = ["etterem", "koltseg_tipus", "osszeg"]
    permission_required = "billing.add_etteremkoltseg"
    success_url = reverse_lazy("billing:koltseg_list")
    template_name = "billing/koltseg_form.html"

class KoltsegUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
    model = EtteremKoltseg
    fields = ["etterem", "koltseg_tipus", "osszeg"]
    permission_required = "billing.change_etteremkoltseg"
    success_url = reverse_lazy("billing:koltseg_list")
    template_name = "billing/koltseg_form.html"

class KoltsegDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
    model = EtteremKoltseg
    permission_required = "billing.delete_etteremkoltseg"
    success_url = reverse_lazy("billing:koltseg_list")
    template_name = "billing/confirm_delete.html"
