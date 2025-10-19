from django.contrib import admin
from .models import EtteremEtelInfo, Mentes

@admin.register(EtteremEtelInfo)
class EtteremEtelInfoAdmin(admin.ModelAdmin):
    list_display = ("etel_thumbnail", "etel", "etterem", "platform", "ar", "szallitas_ido", "felhaszn_ertekelesek", "promocio")
    search_fields = ("etel__nev", "etterem__nev")
    list_filter = ("platform", "etterem__platform")
    autocomplete_fields = ("etel", "etterem")   # <- kell Etel/Etterem admin + search_fields
    ordering = ("etel", "etterem")

    def etel_thumbnail(self, obj):
        if obj.etel and obj.etel.kep_url:
            return f'<img src="{obj.etel.kep_url}" style="height:40px; width:40px; object-fit:cover; border-radius:4px;" />'
        return ''
    etel_thumbnail.allow_tags = True
    etel_thumbnail.short_description = 'Kép'

@admin.register(Mentes)
class MentesAdmin(admin.ModelAdmin):
    list_display = ("felhasznalo", "etel", "letrehozva")
    search_fields = ("felhasznalo__username", "etel__nev")
    autocomplete_fields = ("felhasznalo", "etel")
    ordering = ("-letrehozva",)
