from django import forms
from accounts.models import Account,UserProfile

class RegistrationForm(forms.ModelForm):
    # in form use additional fields
    # in widgets pass attr css like placeholder
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password'
    }))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']


    # override the main init methos to put form-control in all fields attr
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        # pass the specific placeholed to specific field name
        self.fields["first_name"].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields["last_name"].widget.attrs['placeholder'] = 'Enter your last name'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password does not match")
        

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["first_name","last_name","phone_number"]

    # override the main init methos to put form-control in all fields attr
    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False,error_messages={"invalid":{"Image file Only"}},widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ["address_line_1","address_line_2","city","state","country","profile_picture"]


    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

