from django.db import models

class EtteremEtelInfo(models.Model):
    etel = models.ForeignKey("catalog.Etel", on_delete=models.CASCADE, related_name="etterem_info", verbose_name="Étel")
    etterem = models.ForeignKey("catalog.Etterem", on_delete=models.CASCADE, related_name="etel_info", verbose_name="Étterem")
    ar = models.DecimalField("Ár (HUF)", max_digits=10, decimal_places=2)
    szallitas_ido = models.DurationField("Szállítási idő", null=True, blank=True)
    felhaszn_ertekelesek = models.DecimalField("Felhasználói értékelések (átlag)", max_digits=3, decimal_places=2, null=True, blank=True)
    promocio = models.CharField("Promóció", max_length=255, blank=True)
    class Meta:
        verbose_name="Étterem–Étel információ"; verbose_name_plural="Étterem–Étel információk"
        unique_together=("etel","etterem")
        indexes=[models.Index(fields=["etel"]), models.Index(fields=["etterem"])]
    def __str__(self): return f"{self.etel} @ {self.etterem} – {self.ar} Ft"

class Mentes(models.Model):
    felhasznalo = models.ForeignKey("users.Felhasznalo", on_delete=models.CASCADE, related_name="mentesek", verbose_name="Felhasználó")
    etel = models.ForeignKey("catalog.Etel", on_delete=models.CASCADE, related_name="mentesek", verbose_name="Étel")
    letrehozva = models.DateTimeField("Létrehozva", auto_now_add=True)
    class Meta:
        verbose_name="Mentés"; verbose_name_plural="Mentések"
        unique_together=("felhasznalo","etel")
        ordering=["-letrehozva"]
    def __str__(self): return f"{self.felhasznalo} → {self.etel}"
