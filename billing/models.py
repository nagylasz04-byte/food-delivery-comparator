from django.db import models
from catalog.models import Etterem, PLATFORMOK


KOLTSEG_TIPUSOK = (
    ("szallitas", "Szállítás"),
    ("csomagolas", "Csomagolás"),
    ("borravalo", "Borravaló"),
    ("egyeb", "Egyéb"),
)


class EtteremKoltseg(models.Model):
    # costs can be attached to a specific restaurant (etterem) OR to a platform (platform)
    etterem = models.ForeignKey(
        Etterem,
        on_delete=models.CASCADE,
        related_name="koltsegek",
        null=True,
        blank=True,
    )
    platform = models.CharField(max_length=20, choices=PLATFORMOK, blank=True)
    koltseg_tipus = models.CharField(max_length=30, choices=KOLTSEG_TIPUSOK)
    osszeg = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        target = self.etterem.nev if self.etterem else f"Platform: {self.get_platform_display()}"
        return f"{target} - {self.get_koltseg_tipus_display()} ({self.osszeg} Ft)"
