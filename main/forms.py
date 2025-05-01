from django import forms
from .models import ContactMessage, Member

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']


class MemberRegistrationForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone_number', 'membership_code', 'branch']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'membership_code': forms.TextInput(attrs={'placeholder': 'Enter Membership Code (if any)'}),
            'branch': forms.Select(),
        }

    def clean_membership_code(self):
        membership_code = self.cleaned_data.get("membership_code")
        if not membership_code:
            raise forms.ValidationError(
                "You need a membership code to proceed. Please contact your church to get one."
            )
        return membership_code