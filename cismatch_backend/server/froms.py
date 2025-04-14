from django.forms import ModelForm
from django import forms
from .models import Server, ThirdPartyServer

class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = (
            'ip',
            'port',
            'author',
        )

class ThirdPartyServerForm(forms.ModelForm):
    class Meta:
        model = ThirdPartyServer
        fields = ['ip', 'port', 'server_type', 'description']        