from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'autocomplete': 'name'}))
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    message = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={'rows': 6}))
    website = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))
