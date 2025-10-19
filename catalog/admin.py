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
    list_display = ("thumbnail", "nev", "kategoria")
    search_fields = ("nev", "kategoria", "leiras")   # <- fontos az autocomplete-hez
    ordering = ("nev",)
    readonly_fields = ("thumbnail",)

    def thumbnail(self, obj):
        if obj.kep_url:
            return f'<img src="{obj.kep_url}" style="height:48px; width:48px; object-fit:cover; border-radius:4px;" />'
        return ''
    thumbnail.allow_tags = True
    thumbnail.short_description = 'Kép'
