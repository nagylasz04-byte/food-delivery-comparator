from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from foodcompare.mixins import LoginRequired, WritePermissionRequired, StaffRequired
from .models import Felhasznalo
from .forms import FelhasznaloCreationForm, FelhasznaloUpdateForm


# FELHASZNALO CRUD (note: user creation via UI may require special handling for password)
class FelhasznaloListView(StaffRequired, ListView):
    model = Felhasznalo
    template_name = "users/felhasznalo_list.html"


class FelhasznaloDetailView(DetailView):
	model = Felhasznalo
	template_name = "users/felhasznalo_detail.html"


class FelhasznaloCreateView(LoginRequired, WritePermissionRequired, CreateView):
	model = Felhasznalo
	form_class = FelhasznaloCreationForm
	permission_required = "users.add_felhasznalo"
	template_name = "users/felhasznalo_form.html"
	success_url = reverse_lazy("users:felhasznalo_list")


# Public registration view (for new users)
class RegisterView(CreateView):
	model = Felhasznalo
	form_class = FelhasznaloCreationForm
	template_name = "users/felhasznalo_form.html"
	success_url = reverse_lazy("login")

	def dispatch(self, request, *args, **kwargs):
		# redirect authenticated users away from registration page
		if request.user.is_authenticated:
			from django.shortcuts import redirect
			return redirect("home")
		return super().dispatch(request, *args, **kwargs)


class FelhasznaloUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
	model = Felhasznalo
	form_class = FelhasznaloUpdateForm
	permission_required = "users.change_felhasznalo"
	template_name = "users/felhasznalo_form.html"
	success_url = reverse_lazy("users:felhasznalo_list")


class FelhasznaloDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
	model = Felhasznalo
	permission_required = "users.delete_felhasznalo"
	template_name = "compare/confirm_delete.html"
	success_url = reverse_lazy("users:felhasznalo_list")


# JOG CRUD
# NOTE: Jog and FelhJog models removed; corresponding CRUD views were deleted.


# Create your views here.
