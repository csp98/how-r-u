from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from howru_models.models import Question


class QuestionForm(ModelForm):
    privacy = forms.CharField()
    responses_field = forms.CharField()

    class Meta:
        model = Question
        fields = ["text", "public", "language"]

    def clean(self):
        cd = self.cleaned_data
        clean_responses = cd.get("responses_field").replace('\r', '')
        response_list = list()
        for response in clean_responses.split('\n'):
            if response:
                clean_response = response.strip()
                if clean_response:
                    response_list.append(response)
        if len(response_list) < 2:
            raise ValidationError("You must specify at least two possible responses")
        self.cleaned_data['responses'] = response_list
        privacy = cd.get("privacy")
        self.cleaned_data['public'] = privacy == "Public"
