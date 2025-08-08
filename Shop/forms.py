from django import forms
from .models import ItemMaster,ShopMaster,AccessRequest


# Access Request Form 
class AccessRequestForm(forms.ModelForm):
    class Meta:
        model = AccessRequest
        fields = ['full_name', 'company_name', 'email', 'contact_number', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Why do you need access?', 'rows': 4}),
        }
# Item Form
class ItemForm(forms.ModelForm):
    class Meta:
        model = ItemMaster
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Shop Form
class ShopForm(forms.ModelForm):
    class Meta:
        model = ShopMaster
        fields = ['name', 'active_status', 'shop_id','shared_email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'active_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shop_id': forms.TextInput(attrs={'class': 'form-control'}),
            'shared_email':forms.TextInput(attrs={'class': 'form-control'})
        }
