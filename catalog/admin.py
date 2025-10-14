from django.contrib import admin
from .models import Etterem, Etel

@admin.register(Etterem)
class EtteremAdmin(admin.ModelAdmin):
    list_display = ("nev", "cim", "platform")
    list_filter  = ("platform",)
    search_fields = ("nev", "cim")
    ordering = ("nev",)

@admin.register(Etel)
class EtelAdmin(admin.ModelAdmin):
    list_display = ("nev", "kategoria")
    search_fields = ("nev", "kategoria", "leiras")
    ordering = ("nev",)
