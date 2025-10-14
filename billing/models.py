from django.db import models

class EtteremKoltseg(models.Model):
    class KoltsegTipus(models.TextChoices):
        SZALLITAS="szallitas","Szállítás"
        CSOMAGOLAS="csomagolas","Csomagolás"
        BORRAVALO="borravalo","Borravaló"
        EGYEB="egyeb","Egyéb"
    etterem = models.ForeignKey("catalog.Etterem", on_delete=models.CASCADE, related_name="koltsegek", verbose_name="Étterem")
    koltseg_tipus = models.CharField("Költség típusa", max_length=20, choices=KoltsegTipus.choices)
    osszeg = models.DecimalField("Összeg (HUF)", max_digits=10, decimal_places=2)
    class Meta:
        verbose_name="Étterem költség"; verbose_name_plural="Étterem költségek"
        indexes=[models.Index(fields=["koltseg_tipus"])]
    def __str__(self): return f"{self.etterem} – {self.get_koltseg_tipus_display()} = {self.osszeg} Ft"
