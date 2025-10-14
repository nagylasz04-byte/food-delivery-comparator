from django.contrib import admin
from .models import Etterem, Etel

@admin.register(Etterem)
class EtteremAdmin(admin.ModelAdmin):
    list_display = ("nev", "cim", "platform")
    search_fields = ("nev", "cim")            # <- fontos az autocomplete-hez
    list_filter = ("platform",)
    ordering = ("nev",)

@admin.register(Etel)
class EtelAdmin(admin.ModelAdmin):
    list_display = ("nev", "kategoria")
    search_fields = ("nev", "kategoria", "leiras")   # <- fontos az autocomplete-hez
    ordering = ("nev",)
