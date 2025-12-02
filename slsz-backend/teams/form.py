from django import forms

class TeamFilterForm(forms.Form):
    space_id = forms.CharField(max_length=100,required=True)
    teamName = forms.CharField(max_length=30,required=False)
    creator_name = forms.CharField(max_length=20,required=False)  # 队伍创建者的用户ID
    created_at_start = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    created_at_end = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        created_at_start = cleaned_data.get("created_at_start")
        created_at_end = cleaned_data.get("created_at_end")

        if created_at_start and created_at_end and created_at_start > created_at_end:
            self.add_error("created_at_start", "开始日期不能晚于结束日期")