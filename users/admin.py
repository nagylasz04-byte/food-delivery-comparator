from django.contrib import admin
from .models import Felhasznalo, Jog, FelhJog

@admin.register(Felhasznalo)
class FelhasznaloAdmin(admin.ModelAdmin):
    list_display = ("username", "nev", "email", "kedvenc_etterem", "is_active", "is_staff")
    search_fields = ("username", "nev", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")
    autocomplete_fields = ("kedvenc_etterem",)   # <- kell hozzá Etterem admin + search_fields
    ordering = ("username",)

@admin.register(Jog)
class JogAdmin(admin.ModelAdmin):
    list_display = ("nev",)
    search_fields = ("nev",)

@admin.register(FelhJog)
class FelhJogAdmin(admin.ModelAdmin):
    list_display = ("felhasznalo", "jog")
    autocomplete_fields = ("felhasznalo", "jog")
    search_fields = ("felhasznalo__username", "jog__nev")
