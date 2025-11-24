from django.template.defaultfilters import title
from django.views.decorators.http import require_http_methods
from utils import custom_response, decrypt, encrypt, send_email_prompt
from .models import Announcement, AnnouncementReadRecord
from competition_space.models import CompetitionSpace, SpaceUser
from accounts.models import User, Notify
import json


# 发布公告
@require_http_methods(["POST"])
def create_announcement(request):
    try:
        data = json.loads(request.body)
        space_id = int(decrypt(data.get('space_id')))
        title = data.get('title')
        content = data.get('content')

        if not all([space_id, title, content]):
            return custom_response(message="缺少必要的字段", status=400)

        space = CompetitionSpace.objects.get(id=space_id)
        space_user = SpaceUser.objects.get(space=space, user=request.user0)
        if not space_user.is_admin:
            return custom_response(message="没有权限", status=403)

        announcement = Announcement.objects.create(
            space=space,
            title=title,
            content=content,
            created_by=request.user0
        )

        email_list = list(User.objects.filter(space_user__space=space, notify__announcement_notify=True).values_list('email', flat=True))
        if email_list:
            send_email_prompt(email_list=email_list,subject=f"关于{space.title}的公告通知"
                              ,message=f"标题：{title}\n内容：{content}")

        AnnouncementReadRecord.objects.create(space_user=space_user, announcement=announcement)
        return custom_response(data={"announcement_id": encrypt(announcement.id)}, message="公告发布成功",status=200)

    except SpaceUser.DoesNotExist:
        return custom_response(message="该竞赛空间成员不存在", status=404)
    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except User.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    # except Exception as e:
    #     return custom_response(message=f"发布失败: {str(e)}", status=500)


# 更新公告
@require_http_methods(["PUT"])
def update_announcement(request):
    try:
        data = json.loads(request.body)
        announcement_id = int(decrypt(data.get('announcement_id')))
        announcement = Announcement.objects.get(id=announcement_id)

        space = announcement.space
        if not SpaceUser.objects.get(space=space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        email_list = list(
            User.objects.filter(space_user__space=space, notify__announcement_notify=True).values_list('email',flat=True))
        if email_list:
            send_email_prompt(email_list=email_list, subject=f"关于{space.title}的公告更新"
                              , message=f"原公告：\n    标题:{announcement.title}\n    内容:{announcement.content}\n新公告：\n"
                                        f"    标题：{data.get('title',announcement.title)}\n    容：{data.get('content',announcement.content)}")

        announcement.title = data.get('title',announcement.title)
        announcement.content = data.get('content',announcement.content)
        announcement.save()


        # 删除此公告的阅读记录，重新提醒
        AnnouncementReadRecord.objects.filter(announcement=announcement).delete()

        return custom_response(message="公告更新成功", status=200)

    except Announcement.DoesNotExist:
        return custom_response(message="该公告不存在或已被删除", status=404)
    except Exception as e:
        return custom_response(message=f"更新失败: {str(e)}", status=500)


# 删除公告
@require_http_methods(["DELETE"])
def delete_announcement(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=int(decrypt(announcement_id)))
        space = announcement.space
        if not SpaceUser.objects.get(space=space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        announcement.delete()
        return custom_response(message="公告删除成功")

    except Announcement.DoesNotExist:
        return custom_response(message="未找到该公告", status=404)
    except Exception as e:
        return custom_response(message=f"删除失败: {str(e)}", status=500)


# 统计用户未读公告数以及相应的公告ID（按竞赛空间分类）
@require_http_methods(["GET"])
def get_unread_announcement_count(request):
    try:
        user = request.user0
        spaces = CompetitionSpace.objects.filter(space__user=user)
        result = []

        for space in spaces:
            all_announcements = Announcement.objects.filter(space=space)
            read_announcements = AnnouncementReadRecord.objects.filter(space_user__user=user, announcement__space=space).values_list('announcement_id', flat=True)
            unread_announcements = all_announcements.exclude(id__in=read_announcements)
            unread_announcements_ids = list(unread_announcements.values_list('id', flat=True))
            encrypted_ids = [encrypt(announcement_id) for announcement_id in unread_announcements_ids]
            result.append({
                "space_id": encrypt(space.id),
                "space_title": space.title,
                "unread_count": unread_announcements.count(),
                "unread_announcement_ids": encrypted_ids
            })

        return custom_response(data=result,message="获取用户未读公告成功",status=200)

    except User.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Exception as e:
        return custom_response(message=f"查询失败: {str(e)}", status=500)

def get_announcement_by_id(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=int(decrypt(announcement_id)))
        if not SpaceUser.objects.filter(space=announcement.space,user=request.user0).exists():
            return custom_response(message="没有阅读权限", status=403)
        return custom_response(data={"space.title": announcement.space.title,"announcement_title":announcement.title,
                                     "announcement_content": announcement.content,
                                     "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                     "updated_at":announcement.updated_at.strftime("%Y-%m-%d %H:%M:%S")},
                               message="获取公告成功",status=200)
    except Announcement.DoesNotExist:
        return custom_response(message="公告不存在", status=404)
    except Exception as e:
        return custom_response(message="查询失败",status=500)

def get_user_announcements(request):
    try:
        # 获取当前登录用户
        user = request.user0
        # 获取用户加入的所有竞赛空间
        spaces = SpaceUser.objects.filter(user=user).values_list('space_id', flat=True)

        # 获取这些竞赛空间的所有公告
        announcements = Announcement.objects.filter(space__in=spaces).order_by('space__title','-created_at')

        # 按竞赛空间分类公告
        announcements_by_space = {}
        for announcement in announcements:
            space_title = announcement.space.title
            if space_title not in announcements_by_space:
                announcements_by_space[space_title] = []
            announcements_by_space[space_title].append({
                "announcement_id": encrypt(announcement.id),
                "announcement_title": announcement.title,
                "announcement_content": announcement.content,
                "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": announcement.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            })

        # 构造返回数据
        data = [
            {
                "space_title": space_title,
                "announcements": announcements_list,
            }
            for space_title, announcements_list in announcements_by_space.items()
        ]

        return custom_response(data=data, message="获取公告成功", status=200)

    except Exception as e:
        return custom_response(message="查询失败", status=500)

# 标记用户对某个公告已读
@require_http_methods(["POST"])
def mark_announcement_as_read(request,announcement_id):
    try:
        announcement = Announcement.objects.get(id=int(decrypt(announcement_id)))
        space_user = SpaceUser.objects.filter(space=announcement.space, user=request.user0).first()
        AnnouncementReadRecord.objects.get_or_create(space_user=space_user, announcement=announcement)
        return custom_response(message="成功标记为已读", status=200)

    except User.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Announcement.DoesNotExist:
        return custom_response(message="未找到该公告", status=404)
    except Exception as e:
        return custom_response(message=f"标记失败: {str(e)}", status=500)