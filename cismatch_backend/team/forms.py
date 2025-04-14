from django.forms import ModelForm

from .models import Team

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = (
            'title',
            'body',
            'logo',
            'social_url',
            'teammates',
            'author'

        )