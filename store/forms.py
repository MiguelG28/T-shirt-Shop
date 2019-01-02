from django import  forms
from django.core import validators
from django.core.exceptions import ValidationError

from store.models import Cart, Product, Order, Address, OrderProduct
from django.contrib.auth.models import User

class CartForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Cart
        fields = ('quantity','product',)

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['billing_address', 'delivery_address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['billing_address'].queryset = self.fields['billing_address'].queryset.filter(
            user=user)
        self.fields['delivery_address'].queryset = self.fields['delivery_address'].queryset.filter(
            user=user)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'phone', 'nif']
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

def validate_initial_value(value):
    if not value[0].isupper():
        raise ValidationError(
            ('The %s is not in upper case'),
            params={'value': value},
        )


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.', validators=[validate_initial_value])
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.', validators=[validators.MinLengthValidator(2)])
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class EditProfileForm(UserChangeForm):
    template_name = '/something/else'

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )


class AddProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'streamer', 'size', 'color', 'price', 'available', 'stock', 'img']