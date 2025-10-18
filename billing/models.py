from django.db import models
from catalog.models import Etterem


KOLTSEG_TIPUSOK = (
    ("szallitas", "Szállítás"),
    ("csomagolas", "Csomagolás"),
    ("borravalo", "Borravaló"),
    ("egyeb", "Egyéb"),
)


class EtteremKoltseg(models.Model):
    etterem = models.ForeignKey(
        Etterem,
        on_delete=models.CASCADE,
        related_name="koltsegek"  # FONTOS: így tudunk összegezni a termékoldalon
    )
    koltseg_tipus = models.CharField(max_length=30, choices=KOLTSEG_TIPUSOK)
    osszeg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.etterem.nev} - {self.get_koltseg_tipus_display()} ({self.osszeg} Ft)"
