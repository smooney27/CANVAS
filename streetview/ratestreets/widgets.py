from django import forms

class HiddenSelect(forms.Select):
    pass

class LabelOnly(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        return u''
