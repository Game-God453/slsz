import re

from django import forms

from utils import verify_code


class StrictRegisterForm(forms.Form):
    phone_number = forms.CharField(max_length=11, min_length=11)
    code = forms.CharField(max_length=6)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^1[3-9]\d{9}$', phone_number):
            raise forms.ValidationError("手机号格式不正确")
        return phone_number

    def clean_code(self):
        phone = self.cleaned_data.get('phone_number')
        code = self.cleaned_data.get('code')
        if not verify_code(phone, code):
            raise forms.ValidationError("验证码错误")
        return code