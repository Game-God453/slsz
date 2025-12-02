from django import forms

class CompetitionSpaceFilterForm(forms.Form):
    name = forms.CharField(required=False, max_length=50)
    is_active = forms.BooleanField(required=False)
    date_start = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    date_end = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start and date_end and date_start > date_end:
            self.add_error("date_start", "开始日期不能晚于结束日期")