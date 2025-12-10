from django.db import models
import re


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

    def get_city(self) -> str:
        """Attempt to extract a city name from the `cim` (address) field.

        Strategy:
        - If the first token of the address is a numeric postal code, use the next
          token as the city.
        - Otherwise take the very first word of the `cim` (the repo requirement
          is that the city is the first word in the address) and return it.
        - If nothing reliable found, fall back to searching for 'Budapest' or
          the last address segment.
        """
        if not self.cim:
            return ""
        txt = self.cim.strip()
        if not txt:
            return ""
        # Primary rule: first word is the city (handle leading postal codes)
        tokens = re.split(r"\s+", txt)
        if tokens:
            first = tokens[0].strip().strip(',;')
            # If the first token is a postal code (digits), use the next token
            if re.match(r"^\d{3,6}$", first) and len(tokens) > 1:
                first = tokens[1].strip().strip(',;')
            # clean trailing punctuation
            first = re.sub(r"[,:;.-]+$", "", first).strip()
            if first:
                return first

        # Fallbacks
        if "Budapest" in txt:
            return "Budapest"

        parts = [p.strip() for p in re.split(r"[,;\n]", txt) if p.strip()]
        if parts:
            candidate = parts[-1]
            candidate = re.sub(r"^\s*\d{3,6}\s+", "", candidate)
            candidate = candidate.split("-")[0].strip()
            return candidate

        return ""
