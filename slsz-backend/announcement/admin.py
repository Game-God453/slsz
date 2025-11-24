from django.contrib.admin import ModelAdmin
from django.contrib import admin
from accounts.models import User
from competition_space.models import CompetitionSpace
from .models import Announcement, AnnouncementReadRecord


@admin.register(Announcement)
class AnnouncementAdmin(ModelAdmin):
    list_display = ['title', 'space', 'created_by', 'created_at', 'updated_at']
    list_filter = ['space', 'created_by', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-space','-created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user0.role == 'school_super_admin':
            return qs.filter(space__school=request.user0.school)
        return qs

    def has_add_permission(self, request):
        return request.user0.role in ['platform_admin', 'school_super_admin','competition_admin']

    def has_change_permission(self, request, obj=None):
        if request.user0.role in ['platform_admin', 'school_super_admin']:
            return True
        # if obj:
        #     # 获取公告所属的竞赛空间
        #     space = obj.space
        #     # 检查当前用户是否是该竞赛空间的管理员
        #     return SpaceUser.objects.filter(
        #         space=space,
        #         user=request.user,
        #         is_admin=True
        #     ).exists()
        # return False

    def has_delete_permission(self, request, obj=None):
        if request.user0.role in ['platform_admin', 'school_super_admin']:
            return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user0.role == "school_super_admin":

            if db_field.name == "space":
                object_id = request.resolver_match.kwargs.get('object_id')
                if object_id:
                    # 如果是更新公告，固定 created_by 为当前公告的创建者
                    announcement = Announcement.objects.get(pk=object_id)
                    kwargs["queryset"] = CompetitionSpace.objects.filter(school=announcement.space.school)
                else:
                    kwargs["queryset"] = CompetitionSpace.objects.filter(school=request.user0.school)

            if db_field.name == "created_by":
                # 获取当前正在编辑的 Announcement 实例的 space_id
                object_id = request.resolver_match.kwargs.get('object_id')
                if object_id:
                    # 如果是更新公告，固定 created_by 为当前公告的创建者
                    announcement = Announcement.objects.get(pk=object_id)
                    kwargs["queryset"] = User.objects.filter(pk=announcement.created_by.pk)
                else:
                    kwargs["queryset"] = User.objects.filter(school=request.user0.school,role='school_super_admin')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AnnouncementReadRecord)
class AnnouncementReadRecordAdmin(ModelAdmin):
    list_display = ['space_user', 'announcement', 'read_at']
    list_filter = ['space_user', 'announcement', 'read_at']
    search_fields = [ 'announcement__title']
    ordering = ['-read_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user0.role == 'school_super_admin':
            return qs.filter(announcement__space__school=request.user0.school)
        return qs
