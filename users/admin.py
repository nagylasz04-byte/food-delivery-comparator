from django.contrib import admin
from .models import Felhasznalo, Jog, FelhJog

@admin.register(Felhasznalo)
class FelhasznaloAdmin(admin.ModelAdmin):
    list_display=("username","nev","email","kedvenc_etterem","is_active","is_staff")
    search_fields=("username","nev","email")

@admin.register(Jog)
class JogAdmin(admin.ModelAdmin):
    list_display=("nev",)
    search_fields=("nev",)

@admin.register(FelhJog)
class FelhJogAdmin(admin.ModelAdmin):
    list_display=("felhasznalo","jog")
    search_fields=("felhasznalo__username","jog__nev")
