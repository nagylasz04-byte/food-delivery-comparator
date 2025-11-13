from django.contrib import admin
from .models import Felhasznalo


@admin.register(Felhasznalo)
class FelhasznaloAdmin(admin.ModelAdmin):
    list_display = ("username", "nev", "email", "kedvenc_etterem", "is_active", "is_staff")
    search_fields = ("username", "nev", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")
    autocomplete_fields = ("kedvenc_etterem",)   # <- kell hozzá Etterem admin + search_fields
    ordering = ("username",)
