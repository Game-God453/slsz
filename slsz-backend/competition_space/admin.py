from django import forms
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from .models import CompetitionSpace, SpaceUser, School, User


class CompetitionSpaceCreationForm(forms.ModelForm):
    class Meta:
        model = CompetitionSpace
        fields = ('school', 'title', 'description', 'poster', 'category',
                  'level','start_date', 'end_date','created_by')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CompetitionSpaceChangeForm(forms.ModelForm):
    class Meta:
        model = CompetitionSpace
        fields = ('title', 'description', 'poster', 'category',
                  'level', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

@admin.register(CompetitionSpace)
class CompetitionSpaceAdmin(ModelAdmin):
    list_display = ['title', 'school', 'category', 'level', 'start_date', 'end_date', 'created_by', 'is_active']
    list_filter = ['school', 'category', 'level', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['start_date']

    def has_add_permission(self, request):
        """只有 role 为 competition_admin 的用户才能创建 CompetitionSpace"""
        # if request.user0.role == 'competition_admin':
        #     return True
        return True

    def has_change_permission(self, request, obj=None):
        """只有 role 为 competition_admin 的用户才能修改 CompetitionSpace"""
        # if request.user0.role == 'competition_admin':
        #     return True
        return True

    def has_delete_permission(self, request, obj=None):
        """只有 role 为 competition_admin 的用户才能删除 CompetitionSpace"""
        # if request.user0.role == 'competition_admin':
        #     return True
        return True

    def get_form(self, request, obj=None, **kwargs):

        kwargs['form'] = CompetitionSpaceChangeForm if obj else CompetitionSpaceCreationForm
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义 created_by 字段的选项"""
        if request.user0.role == "school_super_admin":

            if db_field.name == "school":
                kwargs["queryset"] = School.objects.filter(id=request.user0.school.id)

            if db_field.name == "created_by":
                kwargs["queryset"] = User.objects.filter(Q(role='competition_admin') | Q(role='school_super_admin'), school=request.user0.school)
                kwargs["to_field_name"] = "username"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """根据用户角色过滤查询结果"""
        qs = super().get_queryset(request)
        if request.user0.role == 'competition_admin':
            return qs.filter(school=request.user0.school)
        return qs

@admin.register(SpaceUser)
class SpaceUserAdmin(ModelAdmin):
    list_display = ['space', 'user', 'realName', 'studentId', 'collegeName', 'is_admin']
    list_filter = ['space', 'is_admin']
    search_fields = ['space__title', 'user__username', 'realName', 'studentId', 'collegeName']
    ordering = ['space']

    def get_queryset(self, request):
        """根据用户角色过滤查询结果"""
        qs = super().get_queryset(request)
        if request.user0.role == 'competition_admin':
            return qs.filter(space__school=request.user0.school)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定义 created_by 字段的选项"""
        if request.user0.role == "school_super_admin":

            if db_field.name == "space":
                kwargs["queryset"] = CompetitionSpace.objects.filter(school=request.user0.school)

            if db_field.name == "user":
                kwargs["queryset"] = User.objects.filter(school=request.user0.school)
                kwargs["to_field_name"] = "username"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

