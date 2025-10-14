from django.contrib import admin
from .models import Etterem, Etel

@admin.register(Etterem)
class EtteremAdmin(admin.ModelAdmin):
    list_display=("nev","platform","cim")
    list_filter=("platform",)
    search_fields=("nev","cim")

@admin.register(Etel)
class EtelAdmin(admin.ModelAdmin):
    list_display=("nev","kategoria")
    search_fields=("nev","kategoria")

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
