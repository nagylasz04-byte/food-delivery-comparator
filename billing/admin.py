from django.contrib import admin
from .models import EtteremKoltseg

@admin.register(EtteremKoltseg)
class EtteremKoltsegAdmin(admin.ModelAdmin):
    list_display = ("etterem", "koltseg_tipus", "osszeg")
    list_filter = ("koltseg_tipus",)
    search_fields = ("etterem__nev",)
    autocomplete_fields = ("etterem",)   # <- ez hivatkozik az Etterem adminra
    ordering = ("etterem", "koltseg_tipus")
