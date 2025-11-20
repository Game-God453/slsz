# your_app_name/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from .models import School, User


class CustomGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return False
            # 只有平台管理员可以访问 School 模型
        return request.user0.role == 'platform_admin'

# 注册 Group 模型
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def has_module_permission(self, request):
        if request.user.is_anonymous:
            return False
            # 只有平台管理员可以访问 School 模型
        return request.user0.role == 'platform_admin'


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone', 'username', 'school', 'email', 'role', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            ('competition_admin', '竞赛负责人'),
            ('student', '普通学生')
        ]
        # self.fields['role'].disabled = True
        # self.fields['school'].disabled = True

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'school')
    list_filter = ('role', 'school')
    search_fields = ('username', 'email', 'phone')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.exclude(id=request.user.id)
        if request.user0.role == 'school_super_admin':
            return qs.filter(school=request.user0.school)
        return qs

    def has_add_permission(self, request):
        return request.user0.role in ['platform_admin', 'school_super_admin']

    def has_change_permission(self, request, obj=None):
        return request.user0.role in ['platform_admin', 'school_super_admin']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.id == request.user.id:
            return False
        return request.user0.role in ['platform_admin', 'school_super_admin']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "school" and request.user0.role == 'school_super_admin':
            kwargs["queryset"] = School.objects.filter(id=request.user0.school.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        if request.user0.role == 'school_super_admin':
            kwargs['form'] = CustomUserChangeForm if obj else CustomUserCreationForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # 如果是新建用户，确保密码被加密
        if not obj.pk:  # 检查是否是新建对象
            password = request.POST.get('password')  # 从 POST 请求中获取密码
            if password:
                obj.set_password(password)  # 加密密码
        super().save_model(request, obj, form, change)