# catalog/models.py
from django.db import models


# --- Platform választék (choices) ---
PLATFORM_WOLT = "wolt"
PLATFORM_FOODORA = "foodora"
PLATFORM_BOLT = "bolt"

PLATFORM_CHOICES = (
    (PLATFORM_WOLT, "Wolt"),
    (PLATFORM_FOODORA, "Foodora"),
    (PLATFORM_BOLT, "Bolt Food"),
)


class Etterem(models.Model):
    nev = models.CharField(max_length=150, verbose_name="Név")
    cim = models.CharField(max_length=255, verbose_name="Cím")
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name="Platform",
        help_text="Pl.: Wolt / Foodora / Bolt Food",
    )

    class Meta:
        verbose_name = "Étterem"
        verbose_name_plural = "Éttermek"
        ordering = ("nev",)

    def __str__(self) -> str:
        return f"{self.nev} ({self.get_platform_display()})"

    def get_platform_url(self) -> str:
        """
        Visszaadja a platform nyitóoldalát a platform kód alapján.
        Ha nincs ismert platform, akkor '#'-t ad vissza.
        (Ez nem igényel migrációt, csak sablonból hívjuk.)
        """
        mapping = {
            PLATFORM_WOLT: "https://wolt.com/hu",
            PLATFORM_FOODORA: "https://www.foodora.hu",
            PLATFORM_BOLT: "https://bolt.eu/hu/food",
        }
        return mapping.get(self.platform, "#")


class Etel(models.Model):
    nev = models.CharField(max_length=150, verbose_name="Név")
    leiras = models.TextField(blank=True, verbose_name="Leírás")
    kategoria = models.CharField(max_length=50, blank=True, verbose_name="Kategória")
    kep_url = models.URLField(blank=True, verbose_name="Kép URL")

    class Meta:
        verbose_name = "Étel"
        verbose_name_plural = "Ételek"
        ordering = ("nev",)

    def __str__(self) -> str:
        return self.nev
