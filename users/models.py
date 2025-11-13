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

    def __str__(self):
        return self.nev or self.username
