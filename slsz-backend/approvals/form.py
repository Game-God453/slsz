from django import forms
from django.utils import timezone

class SpaceMembershipRequestFilterForm(forms.Form):
    space_id = forms.CharField(required=False,max_length=100)  # 竞赛空间ID
    status = forms.ChoiceField(required=False, choices=[
        ('pending', '待处理'),
        ('approved', '通过'),
        ('rejected', '驳回')
    ])
    requested_at_start = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    requested_at_end = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        requested_at_start = cleaned_data.get("requested_at_start")
        requested_at_end = cleaned_data.get("requested_at_end")

        if requested_at_start and requested_at_end and requested_at_start > requested_at_end:
            self.add_error("requested_at_start", "开始日期不能晚于结束日期")


class TeamMembershipRequestFilterForm(forms.Form):
    team_id = forms.IntegerField(required=False)  # 队伍ID
    status = forms.ChoiceField(required=False, choices=[
        ('pending', '待处理'),
        ('approved', '接受'),
        ('rejected', '拒绝')
    ])
    requested_at_start = forms.DateField(required=False, input_formats=["%Y-%m-%d"])
    requested_at_end = forms.DateField(required=False, input_formats=["%Y-%m-%d"])

    def clean(self):
        cleaned_data = super().clean()
        requested_at_start = cleaned_data.get("requested_at_start")
        requested_at_end = cleaned_data.get("requested_at_end")

        if requested_at_start and requested_at_end and requested_at_start > requested_at_end:
            self.add_error("requested_at_start", "开始日期不能晚于结束日期")