from django.db import models

class Etterem(models.Model):
    class PlatformValasztas(models.TextChoices):
        WOLT="wolt","Wolt"; FOODORA="foodora","Foodora"; EGYEB="egyeb","Egyéb"
    nev = models.CharField("Étterm neve", max_length=200)
    cim = models.CharField("Cím", max_length=255, blank=True)
    platform = models.CharField("Platform", max_length=20, choices=PlatformValasztas.choices, default=PlatformValasztas.WOLT)
    class Meta:
        verbose_name="Étterem"; verbose_name_plural="Éttermek"
        indexes=[models.Index(fields=["nev"]), models.Index(fields=["platform"])]
    def __str__(self): return f"{self.nev} ({self.get_platform_display()})"

class Etel(models.Model):
    nev = models.CharField("Étel neve", max_length=200)
    leiras = models.TextField("Leírás", blank=True)
    kategoria = models.CharField("Kategória", max_length=120, blank=True)
    kep_url = models.URLField("Kép URL", blank=True)
    class Meta:
        verbose_name="Étel"; verbose_name_plural="Ételek"
        indexes=[models.Index(fields=["nev","kategoria"])]
    def __str__(self): return self.nev
