from datetime import datetime

from django.core.files.storage import default_storage
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from utils import custom_response, encrypt, decrypt
from .form import CompetitionSpaceFilterForm
from .models import CompetitionSpace, SpaceUser
from accounts.models import User
import json


# 创建竞赛空间
@require_http_methods(["POST"])
def create_competition_space(request):
    try:
        creator = request.user0

        if creator.role != "competition_admin":
            return custom_response(message="不是竞赛负责人，没有权限",status=403)

        school = creator.school
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        level = request.POST.get('level')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        if not all([title, category, level, start_date, end_date]):
            return custom_response(message="缺少必填字段", status=400)

        competition_space = CompetitionSpace.objects.create(
            school=school,
            title=title,
            description=description,
            category=category,
            level=level,
            start_date=start_date,
            end_date=end_date,
            created_by=creator,
            is_active=True
        )
        poster = request.FILES.get('poster')
        if poster:
            competition_space.poster = poster
            competition_space.save()

        # 默认创建者为管理员
        SpaceUser.objects.create(
            space=competition_space,
            user=creator,
            realName=creator.username,
            is_admin=True
        )

        return custom_response(data={"space_id": encrypt(competition_space.id)}, message="竞赛空间创建成功")

    except Exception as e:
        return custom_response(message=f"创建失败：{str(e)}", status=500)


# 删除竞赛空间
@require_http_methods(["POST"])
def close_competition_space(request,space_id):
    try:
        competition_space = CompetitionSpace.objects.get(id=int(decrypt(space_id)))

        if not SpaceUser.objects.get(space=competition_space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        if competition_space.poster:
            old_poster_path = competition_space.poster.path
            if default_storage.exists(old_poster_path):
                default_storage.delete(old_poster_path)

        competition_space.delete()
        return custom_response(message="竞赛空间已删除",status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except Exception as e:
        return custom_response(message=f"关闭失败：{str(e)}", status=500)


# 更新竞赛空间相关信息
@require_http_methods(["POST"])
def update_competition_space(request):
    try:
        space_id = int(decrypt(request.POST.get("space_id")))
        competition_space = CompetitionSpace.objects.get(id=space_id)

        if not SpaceUser.objects.get(space=competition_space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        new_poster = request.FILES.get('poster', competition_space.poster)
        if new_poster:
            if competition_space.poster:
                old_poster_path = competition_space.poster.path
                if default_storage.exists(old_poster_path):
                    default_storage.delete(old_poster_path)
            competition_space.poster = new_poster

        competition_space.title = request.POST.get('title', competition_space.title)
        competition_space.description = request.POST.get('description', competition_space.description)
        competition_space.category = request.POST.get('category', competition_space.category)
        competition_space.level = request.POST.get('level', competition_space.level)
        competition_space.start_date = request.POST.get('start_date', competition_space.start_date)
        competition_space.end_date = request.POST.get('end_date', competition_space.end_date)

        competition_space.save()
        return custom_response(message="竞赛空间信息更新成功",status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    # except Exception as e:
    #     return custom_response(message=f"更新失败：{str(e)}", status=500)


# 添加某个用户为竞赛空间管理员
@require_http_methods(["POST"])
def add_admin_to_competition_space(request):
    try:
        space_id = int(decrypt(request.POST.get("space_id")))
        target_user_id = int(decrypt(request.POST.get("target_user_id")))
        competition_space = CompetitionSpace.objects.get(id=space_id)
        target_user = User.objects.get(id=target_user_id)

        if not SpaceUser.objects.get(space=competition_space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        space_user, created = SpaceUser.objects.get_or_create(space=competition_space, user=target_user)
        space_user.is_admin = True
        space_user.save()

        return custom_response(message="用户已添加为管理员")

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except User.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Exception as e:
        return custom_response(message=f"操作失败：{str(e)}", status=500)


# 移除某个用户退出竞赛空间
@require_http_methods(["POST"])
def remove_user_from_competition_space(request):
    try:
        space_id = int(decrypt(request.POST.get("space_id")))
        target_user_id = int(decrypt(request.POST.get("target_user_id")))
        competition_space = CompetitionSpace.objects.get(id=space_id)
        target_user = User.objects.get(id=target_user_id)

        if not SpaceUser.objects.get(space=competition_space, user=request.user0).is_admin:
            return custom_response(message="没有权限", status=403)

        if SpaceUser.objects.get(space=competition_space, user=target_user).is_admin and request.user0 != competition_space.created_by:
            return custom_response(message="没有权限", status=403)

        SpaceUser.objects.filter(space=competition_space, user=target_user).delete()

        return custom_response(message="用户已从竞赛空间移除")

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except User.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Exception as e:
        return custom_response(message=f"操作失败：{str(e)}", status=500)


# 列出筛选后的所有竞赛空间
@require_http_methods(["POST"])
def list_competition_spaces(request):
    try:
        # 解析前端传入的 JSON 数据
        data = json.loads(request.body)

        # 使用表单验证和清洗数据
        form = CompetitionSpaceFilterForm(data)
        if not form.is_valid():
            return custom_response(message="无效的筛选条件", status=400)

        # 获取清洗后的数据
        cleaned_data = form.cleaned_data
        name = cleaned_data.get("name")
        is_active = cleaned_data.get("is_active")
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        # 构建查询条件
        query = CompetitionSpace.objects.all()

        # 使用 Q 对象构建复杂的查询条件
        conditions = Q()
        if name:
            conditions &= Q(title__icontains=name)
        if is_active is not None:
            conditions &= Q(is_active=is_active)
        if date_start:
            conditions &= Q(start_date__gte=datetime.combine(date_start, datetime.min.time()))
        if date_end:
            conditions &= Q(end_date__lte=datetime.combine(date_end, datetime.max.time()))

        # 应用查询条件
        query = query.filter(conditions)

        # 将查询结果序列化为列表
        competition_spaces_data = [
            {
                "id": encrypt(space.id),
                "title": space.title,
                "description": space.description,
                "poster_url": request.build_absolute_uri(space.poster.url) if space.poster else None,
                "category": space.category,
                "level": space.level,
                "start_date": space.start_date.isoformat(),
                "end_date": space.end_date.isoformat(),
                "is_active": space.is_active,
            }
            for space in query
        ]

        return custom_response(data=competition_spaces_data, message="成功获取竞赛空间列表")

    except json.JSONDecodeError:
        return custom_response(message="无效的 JSON 格式", status=400)
    except Exception as e:
        return custom_response(message=f"查询失败：{str(e)}", status=500)


def get_space_info(request, space_id):
    try:
        space = CompetitionSpace.objects.get(id=int(decrypt(space_id)))
        if not SpaceUser.objects.filter(space=space, user=request.user0).exists():
            return custom_response(message="您没有权限获取该空间的用户信息", status=403)

        space_data={
            "title": space.title,
            "description": space.description,
            "poster":request.build_absolute_uri(space.poster.url) if space.poster else None,
            "category": space.category,
            "level": space.level,
            "start_date": space.start_date.isoformat(),
            "end_date": space.end_date.isoformat(),
        }
        return custom_response(data=space_data,message="获取竞赛空间信息成功", status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except Exception as e:
        return custom_response(message=f"获取用户列表失败：{str(e)}", status=500)


# 列出竞赛空间内的成员名单
@require_http_methods(["GET"])
def list_competition_space_users(request, space_id):
    try:
        # 获取竞赛空间对象
        competition_space = CompetitionSpace.objects.get(id=int(decrypt(space_id)))

        # 检查请求发起者是否为该竞赛空间的成员
        if not SpaceUser.objects.filter(space=competition_space, user=request.user0).exists():
            return custom_response(message="您没有权限获取该空间的用户信息", status=403)

        # 获取该竞赛空间的所有用户
        space_users = SpaceUser.objects.filter(space=competition_space).order_by('-is_admin')

        # 将用户信息序列化为列表
        user_data = [
            {
                "space_user_id":encrypt(su.id),
                "user_avatar":request.build_absolute_uri(su.user.avatar.url) if su.user.avatar else None,
                "realName": su.realName,
                "studentId": su.studentId,
                "collegeName": su.collegeName,
                "is_admin": su.is_admin
            }
            for su in space_users
        ]

        return custom_response(data=user_data, message="成功获取用户列表",status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except Exception as e:
        return custom_response(message=f"获取用户列表失败：{str(e)}", status=500)

# 获取竞赛空间内的个人信息
@require_http_methods(["GET"])
def get_space_user_info(request, space_id):
    try:
        space = CompetitionSpace.objects.get(id=int(decrypt(space_id)))
        space_user = SpaceUser.objects.get(space=space, user=request.user0)
        data = {
            "avatar": request.build_absolute_uri(space_user.user.avatar.url) if space_user.user.avatar else None,
            "realName": space_user.realName,
            "studentId": space_user.studentId,
            "collegeName": space_user.collegeName,
            "phone": space_user.phoneNumber,
            "email": space_user.email,
            "gender": space_user.gender,
        }
        return custom_response(data=data,message="获取竞赛空间个人信息成功", status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="竞赛空间不存在", status=404)
    except SpaceUser.DoesNotExist:
        return custom_response(message="该竞赛空间用户不存在", status=404)
    except Exception as e:
        return custom_response(message="获取信息失败", status=500)

# 修改竞赛空间内的个人信息
@require_http_methods(["POST"])
def edit_space_user_profile(request):
    try:
        space_id = int(decrypt(request.POST.get("space_id")))
        # 获取竞赛空间对象
        competition_space = CompetitionSpace.objects.get(id=space_id)
        # 获取用户对象
        space_user = SpaceUser.objects.get(space=competition_space, user_id=request.user0)

        space_user.realName = request.POST.get("realName", space_user.realName)
        space_user.studentId = request.POST.get("studentId", space_user.studentId)
        space_user.collegeName = request.POST.get("collegeName", space_user.collegeName)

        gender = request.POST.get('gender')
        if gender and (gender != "男" and gender != "女"):
            return custom_response(message="性别只能是男或女", status=400)
        if gender == "男":
            gender = "male"
        elif gender == "女":
            gender = "female"
        space_user.gender = gender if gender else space_user.gender

        space_user.phoneNumber = request.POST.get("phoneNumber", space_user.phoneNumber)
        space_user.email = request.POST.get("email", space_user.email)
        space_user.save()

        return custom_response(message="用户信息已更新",status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except SpaceUser.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Exception as e:
        return custom_response(message=f"更新用户信息失败：{str(e)}", status=500)

# 获取用户加入的所有竞赛空间
@require_http_methods(["GET"])
def get_user_competition_spaces(request):
    try:
        user = request.user0
        spaces = CompetitionSpace.objects.filter(
            space__user=user
        )

        # 将竞赛空间信息序列化为列表
        space_list = [
            {
                "id": encrypt(space.id),
                "title": space.title,
                "description": space.description,
                "poster_url": request.build_absolute_uri(space.poster.url) if space.poster else None,
                "category": space.category,
                "level": space.level,
                "start_date": space.start_date,
                "end_date": space.end_date,
                "is_active": space.is_active

            }
            for space in spaces
        ]

        # 返回统一格式的 JSON 响应
        return custom_response(data=space_list, message="获取成功",status=200)

    except Exception as e:
        # 捕获异常并返回错误信息
        return custom_response(message=f"发生错误：{str(e)}", status=500)
