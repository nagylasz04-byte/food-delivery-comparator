from django.contrib.auth.models import AbstractUser
from django.db import models

class Felhasznalo(AbstractUser):
    nev = models.CharField("Név", max_length=150, blank=True)
    kedvenc_etterem = models.ForeignKey(
        "catalog.Etterem", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="kedvelok",
        verbose_name="Kedvenc étterem",
    )
    class Meta:
        verbose_name = "Felhasználó"
        verbose_name_plural = "Felhasználók"
    def __str__(self): return self.nev or self.username

class Jog(models.Model):
    nev = models.CharField("Jog megnevezése", max_length=100, unique=True)
    class Meta:
        verbose_name = "Jog"; verbose_name_plural = "Jogok"
    def __str__(self): return self.nev

class FelhJog(models.Model):
    felhasznalo = models.ForeignKey("users.Felhasznalo", on_delete=models.CASCADE, related_name="felh_jogok")
    jog = models.ForeignKey("users.Jog", on_delete=models.CASCADE, related_name="felh_jogok")
    class Meta:
        verbose_name = "Felhasználó–Jog"; verbose_name_plural = "Felhasználó–Jog kapcsolatok"
        unique_together = ("felhasznalo", "jog")
    def __str__(self): return f"{self.felhasznalo} ↔ {self.jog}"
