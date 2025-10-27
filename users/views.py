from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from foodcompare.mixins import LoginRequired, WritePermissionRequired, StaffRequired
from .models import Felhasznalo, Jog, FelhJog
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
class JogListView(StaffRequired, ListView):
	model = Jog
	template_name = "users/jog_list.html"


class JogDetailView(DetailView):
	model = Jog
	template_name = "users/jog_detail.html"


class JogCreateView(LoginRequired, WritePermissionRequired, CreateView):
	model = Jog
	fields = ["nev"]
	permission_required = "users.add_jog"
	template_name = "users/jog_form.html"
	success_url = reverse_lazy("users:jog_list")


class JogUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
	model = Jog
	fields = ["nev"]
	permission_required = "users.change_jog"
	template_name = "users/jog_form.html"
	success_url = reverse_lazy("users:jog_list")


class JogDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
	model = Jog
	permission_required = "users.delete_jog"
	template_name = "compare/confirm_delete.html"
	success_url = reverse_lazy("users:jog_list")


# FELHJOG CRUD
class FelhJogListView(StaffRequired, ListView):
	model = FelhJog
	template_name = "users/felhjog_list.html"


class FelhJogDetailView(DetailView):
	model = FelhJog
	template_name = "users/felhjog_detail.html"


class FelhJogCreateView(LoginRequired, WritePermissionRequired, CreateView):
	model = FelhJog
	fields = ["felhasznalo", "jog"]
	permission_required = "users.add_felhjog"
	template_name = "users/felhjog_form.html"
	success_url = reverse_lazy("users:felhjog_list")


class FelhJogUpdateView(LoginRequired, WritePermissionRequired, UpdateView):
	model = FelhJog
	fields = ["felhasznalo", "jog"]
	permission_required = "users.change_felhjog"
	template_name = "users/felhjog_form.html"
	success_url = reverse_lazy("users:felhjog_list")


class FelhJogDeleteView(LoginRequired, WritePermissionRequired, DeleteView):
	model = FelhJog
	permission_required = "users.delete_felhjog"
	template_name = "compare/confirm_delete.html"
	success_url = reverse_lazy("users:felhjog_list")


# Create your views here.
