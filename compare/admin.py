from django.contrib import admin
from .models import EtteremEtelInfo, Mentes

@admin.register(EtteremEtelInfo)
class EtteremEtelInfoAdmin(admin.ModelAdmin):
    list_display = ("etel", "etterem", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio")
    search_fields = ("etel__nev", "etterem__nev")
    list_filter = ("etterem__platform",)
    autocomplete_fields = ("etel", "etterem")   # <- kell Etel/Etterem admin + search_fields
    ordering = ("etel", "etterem")

@admin.register(Mentes)
class MentesAdmin(admin.ModelAdmin):
    list_display = ("felhasznalo", "etel", "letrehozva")
    search_fields = ("felhasznalo__username", "etel__nev")
    autocomplete_fields = ("felhasznalo", "etel")
    ordering = ("-letrehozva",)
