from django import forms


class NameForm(forms.Form):
    """Form for entering user's name before starting the quiz"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'আপনার নাম লিখুন',
            'required': True,
            'autofocus': True
        }),
        label='আপনার নাম'
    )

