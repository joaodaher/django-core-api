from django.db import models

from django_core_api.models import BaseModel, SoftDeleteModel, InheritanceModel
from test_app import managers
from test_app.storage import StoragePath


class Wizard(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    age = models.IntegerField(
        null=True,
        blank=True,
    )
    is_half_blood = models.BooleanField(default=True)
    picture = models.FileField(
        **StoragePath.media_thumb(),
        null=True,
        blank=True,
    )
    house = models.ForeignKey(
        to='test_app.House',
        related_name='wizards',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    spells = models.ManyToManyField(
        to='test_app.Spell',
        through='SpellCast',
        related_name='wizards',
    )
    received_letter_at = models.DateTimeField(
        blank=True,
        null=True,
    )


class House(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    points_boost = models.DecimalField(
        default=1.0,
        decimal_places=2,
        max_digits=4,
    )


class Patronus(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    color = models.CharField(
        max_length=50,
        null=True,
    )
    wizard = models.OneToOneField(
        to='test_app.Wizard',
        on_delete=models.CASCADE,
    )


class Teacher(Wizard):
    is_ghost = models.BooleanField(
        default=False,
    )

    class Meta(Wizard.Meta):
        indexes = []

    objects = models.Manager()
    availables = managers.AvailableManager()


class Spell(InheritanceModel):
    name = models.CharField(
        max_length=50,
    )


class CombatSpell(Spell):
    is_attack = models.BooleanField(default=True)


class EnvironmentalSpell(Spell):
    pass


class SpellCast(BaseModel):
    wizard = models.ForeignKey(
        to='test_app.Wizard',
        on_delete=models.CASCADE,
        related_name='spell_casts',
    )
    spell = models.ForeignKey(
        to='test_app.Spell',
        on_delete=models.CASCADE,
        related_name='spell_casts',
    )
    is_successful = models.BooleanField(
        default=True,
    )


class Wand(BaseModel):
    name = models.CharField(
        max_length=50,
    )
    holder = models.ForeignKey(
        to='test_app.Wizard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wands',
    )


class Memory(SoftDeleteModel):
    owner = models.ForeignKey(
        to='test_app.Wizard',
        on_delete=models.CASCADE,
        related_name='memories',
    )
    description = models.TextField()
