from django.db import models


class Etel(models.Model):
    nev = models.CharField(max_length=150)
    leiras = models.TextField(blank=True)
    kategoria = models.CharField(max_length=50, blank=True)
    kep_url = models.URLField(blank=True)

    def __str__(self):
        return self.nev


PLATFORMOK = (
    ("wolt", "Wolt"),
    ("foodora", "Foodora"),
    ("bolt", "Bolt Food"),
    ("egyeb", "Egyéb"),
)


class Etterem(models.Model):
    nev = models.CharField(max_length=150)
    cim = models.CharField(max_length=250, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORMOK, default="egyeb")

    # ÚJ mezők a termékoldalhoz
    platform_logo_url = models.URLField(blank=True)
    platform_url = models.URLField(blank=True)

    def __str__(self):
        return self.nev

    # Alap logó, ha nincs kitöltve
    def get_platform_logo_url(self) -> str:
        if self.platform_logo_url:
            return self.platform_logo_url
        defaults = {
            "wolt": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Wolt_logo.png",
            "foodora": "https://upload.wikimedia.org/wikipedia/commons/2/26/Foodora_logo.png",
            "bolt": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Bolt_logo.png",
            "egyeb": "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg",
        }
        return defaults.get(self.platform, defaults["egyeb"])

    # Alap platform URL, ha nincs kitöltve
    def get_platform_url(self) -> str:
        if self.platform_url:
            return self.platform_url
        defaults = {
            "wolt": "https://wolt.com",
            "foodora": "https://www.foodora.hu",
            "bolt": "https://bolt.eu/hu",
            "egyeb": "#",
        }
        return defaults.get(self.platform, "#")
