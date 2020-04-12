from rest_framework.fields import IntegerField

from django_core_api import serializers
from test_app import models


class HouseSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.House
        fields = (
            'id',
            'name',
            'points_boost',
            'created_at',
        )
        read_only_fields = (
            'id',
            'created_at',
        )


class HouseStatsSerializer(HouseSerializer):
    wizard_count = IntegerField(read_only=True)

    class Meta(HouseSerializer.Meta):
        fields = HouseSerializer.Meta.fields + (
            'wizard_count',
        )


class WizardShortSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = (
            'name',
            'is_half_blood',
        )


class WizardSerializer(WizardShortSerializer):
    house_id = serializers.ForeignKeyField(queryset=models.House.objects.all())
    house = HouseSerializer(read_only=True)

    class Meta(WizardShortSerializer.Meta):
        fields = (
            'id',
            'created_at',
            'updated_at',
            'name',
            'age',
            'is_half_blood',
            'picture',
            'house_id',
            'house',
        )


class WizardCreatorSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = (
            'name',
            'age',
            'is_half_blood',
        )


class WizardUpdaterSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Wizard
        fields = (
            'age',
        )


class PatronusSerializer(serializers.BaseModelSerializer):
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all())
    wizard = WizardShortSerializer(read_only=True)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Patronus
        fields = (
            'wizard_id',
            'wizard',

            'id',
            'name',
            'color',
        )


class TeacherSerializer(WizardSerializer):
    class Meta(WizardSerializer.Meta):
        model = models.Teacher
        fields = WizardSerializer.Meta.fields + (
            'is_ghost',
        )


class SpellSerializer(serializers.BaseModelSerializer):
    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.Spell
        fields = '__all__'


class SpellCastSerializer(serializers.BaseModelSerializer):
    wizard_id = serializers.ForeignKeyField(queryset=models.Wizard.objects.all())
    wizard = WizardSerializer(read_only=True)

    spell_id = serializers.ForeignKeyField(queryset=models.Spell.objects.all())
    spell = SpellSerializer(read_only=True)

    class Meta(serializers.BaseModelSerializer.Meta):
        model = models.SpellCast
        fields = (
            'id',
            'wizard_id',
            'wizard',
            'spell_id',
            'spell',
            'is_successful',
        )
