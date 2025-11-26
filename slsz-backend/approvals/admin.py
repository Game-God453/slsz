from django import forms
from django.contrib import admin
from .models import SpaceMembershipRequest, CompetitionSpace, User


class SpaceMembershipRequestHandleForm(forms.ModelForm):
    class Meta:
        model = SpaceMembershipRequest
        fields = ('status', 'rejection_reason','need_to_notify')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('pending', '待处理'),
            ('approved', '接受'),
            ('rejected', '拒绝')
        ]

@admin.register(SpaceMembershipRequest)
class SpaceMembershipRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'space', 'realName', 'studentId', 'collegeName', 'status', 'rejection_reason', 'need_to_notify', 'requested_at')
    list_filter = ('space','status', 'requested_at')
    search_fields = ('user__username', 'user__email', 'realName', 'studentId', 'collegeName')
    ordering = ('space','status','-requested_at',)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = SpaceMembershipRequestHandleForm
        return super().get_form(request, obj, **kwargs)

    # 自定义字段的显示方式
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user0.role == "school_super_admin":

            if db_field.name == "space":
                # 只显示当前用户有权限查看的空间
                kwargs["queryset"] = CompetitionSpace.objects.filter(school=request.user0.school)

            if db_field.name == "user":
                # 只显示当前用户所在学校的学生
                kwargs["queryset"] = User.objects.filter(school=request.user0.school)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # 只允许管理员和竞赛空间创建者查看和管理请求
    def has_add_permission(self, request, obj=None):
        return request.user0.role in ['platform_admin', 'school_super_admin']

    def has_change_permission(self, request, obj=None):
        return request.user0.role in ['platform_admin', 'school_super_admin']

    def has_delete_permission(self, request, obj=None):
        return request.user0.role in ['platform_admin', 'school_super_admin']