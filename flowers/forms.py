from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOISE = (
    ("S", "Stripe"),
    ('P', "Paypal")
)

class CheckOutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": '1234 Main St',
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Apartment or suite",
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': "custom-select d-block w-100",
        })
    )
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control"
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOISE)

class PromoCodeForm(forms.Form):
    promocode = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'type': "text",
        'class': "form-control",
        "placeholder": "Promo code",
        'aria - label': "Recipient's username",
        'aria - describedby': "basic-addon2",
    }))
