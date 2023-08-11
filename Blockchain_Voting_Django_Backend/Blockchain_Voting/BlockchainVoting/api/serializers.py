from rest_framework import serializers
import json
from .models import Voter, Election, Choice


class VoterSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = [
            "id",
            "name",
            "user_email",
            "password",
            "admin",
            "voted_in",
        ]


class ElectionSerializer(serializers.ModelSerializer):
    choices_name = serializers.SerializerMethodField()

    def get_choices_name(self, instance):
        result = []
        for choice in instance.choices.all():
            result.append(choice.name)
        return result

    class Meta:
        model = Election
        fields = [
            "id",
            "title",
            "number_of_choices",
            "choices",
            "choices_name",
            "number_of_votes",
            "created",
        ]


class ChoiceSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            "name",
            "choice_id",
        ]


class ElectionUserSerializer(serializers.ModelSerializer):
    choices_name = serializers.SerializerMethodField()
    has_voted = serializers.SerializerMethodField()

    def get_has_voted(self, instance):
        voter_instance = Voter.objects.get(pk=self.context.get("voter_id"))
        if voter_instance.voted_in.contains(instance):
            return True
        return False

    def get_choices_name(self, instance):
        result = []
        for choice in instance.choices.all():
            result.append(choice.name)
        return result

    class Meta:
        model = Election
        fields = [
            "id",
            "title",
            "number_of_choices",
            "choices",
            "choices_name",
            "number_of_votes",
            "has_voted",
            "created",
            "running",
        ]
