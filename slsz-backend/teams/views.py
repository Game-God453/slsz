from datetime import datetime

from django.db.models import Q
from django.views.decorators.http import require_http_methods

from utils import custom_response, decrypt, encrypt
from .form import TeamFilterForm
from .models import Team
from accounts.models import User
from competition_space.models import CompetitionSpace, SpaceUser
import json

# 创建队伍
@require_http_methods(["POST"])
def create_team(request):
    try:
        data = json.loads(request.body)
        space_id = int(decrypt(data.get('space_id')))
        team_name = data.get('teamName')
        demand = data.get('demand')
        target_number = data.get('targetNumber')

        if not all([space_id, team_name]):
            return custom_response(message="缺少必填字段", status=400)

        space = CompetitionSpace.objects.get(id=space_id)
        creator = SpaceUser.objects.get(space=space, user=request.user0)

        if creator.is_captain:
            return custom_response(message="已在该竞赛空间创建队伍，不允许创建多个队伍", status=400)

        team = Team.objects.create(
            space=space,
            teamName=team_name,
            created_by=creator.user,
            demand=demand,
            target_number=target_number,
        )
        # 将创建者自动加入队伍
        creator.team = team
        creator.is_captain = True
        creator.save()
        return custom_response(data={"team_id": encrypt(team.id)}, message="队伍创建成功",status=200)

    except SpaceUser.DoesNotExist:
        return custom_response(message="未在该竞赛空间找到用户", status=404)
    except CompetitionSpace.DoesNotExist:
        return custom_response(message="未找到该竞赛空间", status=404)
    except Exception as e:
        return custom_response(message=f"创建失败：{str(e)}", status=500)


# 解散队伍（从数据库中删除）
@require_http_methods(["DELETE"])
def dissolve_team(request, team_id):
    try:
        team = Team.objects.get(id=int(decrypt(team_id)))
        space_user = SpaceUser.objects.filter(space=team.space, user=request.user0).first()
        if not space_user.is_captain:
            return custom_response(message="没有权限", status=403)

        space_user.is_captain = False
        space_user.save()
        team.delete()
        return custom_response(message="队伍已解散",status=200)

    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except Exception as e:
        return custom_response(message=f"解散失败：{str(e)}", status=500)

# 队长更新队伍相关信息
@require_http_methods(["POST"])
def update_team(request):
    try:
        team_id = int(decrypt(request.POST.get('team_id')))
        team = Team.objects.get(id=team_id)
        if not SpaceUser.objects.get(space=team.space, user=request.user0).is_captain:
            return custom_response(message="没有权限", status=403)

        team.teamName = request.POST.get('teamName', team.teamName)
        team.demand = request.POST.get('demand', team.demand)
        team.target_number = request.POST.get('targetNumber', team.target_number)
        team.qq = request.POST.get('qq', team.qq)
        team.save()

        return custom_response(message="队伍信息更新成功")

    except SpaceUser.DoesNotExist:
        return custom_response(message="未在该竞赛空间找到用户", status=404)
    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except Exception as e:
        return custom_response(message=f"更新失败：{str(e)}", status=500)

# 队员离开队伍
@require_http_methods(["POST"])
def leave_team(request, team_id):
    try:
        team = Team.objects.get(id=int(decrypt(team_id)))
        user = request.user0

        # 检查该用户是否是队伍成员
        member = SpaceUser.objects.get(space=team.space, user=user, team=team)

        # 如果是队长，不允许直接离开，需要先解散队伍或移交队长职务
        if member.is_captain:
            return custom_response(message="队长不能直接离开队伍，请先解散队伍", status=400)

        # 移除该成员
        member.team = None
        member.save()

        return custom_response(message="队员已成功离开队伍")

    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except SpaceUser.DoesNotExist:
        return custom_response(message="不是该队伍成员，无效操作", status=404)
    except Exception as e:
        return custom_response(message=f"离开队伍失败：{str(e)}", status=500)

# 移除某个队员
@require_http_methods(["POST"])
def remove_member(request):
    try:
        team_id = int(decrypt(request.POST.get("team_id")))
        target_spaceUser_id = int(decrypt(request.POST.get("target_space_user_id")))
        team = Team.objects.get(id=team_id)
        if not SpaceUser.objects.filter(space=team.space, user=request.user0).first().is_captain:
            return custom_response(message="没有权限", status=403)

        target_spaceUser = SpaceUser.objects.get(id=target_spaceUser_id)

        if target_spaceUser.user == request.user0:
            return custom_response(message="不能移除自己", status=400)

        target_spaceUser.team = None
        target_spaceUser.save()

        return custom_response(message="队员已从队伍中移除")

    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except SpaceUser.DoesNotExist:
        return custom_response(message="未找到该用户", status=404)
    except Exception as e:
        return custom_response(message=f"移除失败：{str(e)}", status=500)


# 开启招募或停止招募
@require_http_methods(["POST"])
def recruit_or_not(request):
    try:
        data = json.loads(request.body)
        team_id = int(decrypt(data.get("team_id")))
        team = Team.objects.get(id=team_id)
        if not SpaceUser.objects.filter(space=team.space, user=request.user0).first().is_captain:
            return custom_response(message="没有权限", status=403)
        is_recruiting = data.get('recruit', team.is_recruiting)
        if is_recruiting and team.is_recruiting:
            return custom_response(message="已在招募队友中，请勿重复操作", status=400)
        if not is_recruiting and not team.is_recruiting:
            return custom_response(message="已停止招募队友，请勿重复操作", status=400)
        if team.is_locked:
            return custom_response(message="该队伍已锁定，请先解锁",status=400)

        team.is_recruiting = is_recruiting
        team.save()
        return custom_response(message="操作成功",status=200)

    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)

# 锁定或解锁队伍
@require_http_methods(["POST"])
def lock_or_unlock_teamMembers(request):
    try:
        data = json.loads(request.body)
        team_id = int(decrypt(data.get("team_id")))
        team = Team.objects.get(id=team_id)
        if not SpaceUser.objects.filter(space=team.space, user=request.user0).first().is_captain:
            return custom_response(message="没有权限", status=403)
        locked = data.get('lock', team.is_locked)
        if locked and team.is_locked:
            return custom_response(message="以锁定队伍，请勿重复操作", status=400)
        if not locked and not team.is_locked:
            return custom_response(message="以解锁队伍，请勿重复操作", status=400)
        if locked:
            team.is_recruiting = False

        team.is_locked = locked
        team.save()
        return custom_response(message="操作成功", status=200)

    except Team.DoesNotExist:
        return custom_response(message="未找到该队伍", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["POST"])
def list_recruiting_teams(request):
    try:
        # 解析前端传入的 JSON 数据
        data = json.loads(request.body)

        # 使用表单验证和清洗数据
        form = TeamFilterForm(data)
        if not form.is_valid():
            return custom_response(message="无效的筛选条件", status=400)

        # 获取清洗后的数据
        cleaned_data = form.cleaned_data

        space_id = int(decrypt(cleaned_data.get("space_id")))
        space = CompetitionSpace.objects.get(id=space_id)

        teamName = cleaned_data.get("teamName")
        creator_name = cleaned_data.get("creator_name")
        created_at_start = cleaned_data.get("created_at_start")
        created_at_end = cleaned_data.get("created_at_end")

        # 构建查询条件
        query = Team.objects.filter(space=space,is_recruiting=True)  # 只筛选正在招募队员的队伍

        conditions = Q()
        if creator_name:
            conditions &= Q(members__in=SpaceUser.objects.filter(space=space, realName=creator_name))
        if teamName:
            conditions &= Q(teamName__icontains=teamName)
        if created_at_start:
            conditions &= Q(created_at__gte=datetime.combine(created_at_start, datetime.min.time()))
        if created_at_end:
            conditions &= Q(created_at__lte=datetime.combine(created_at_end, datetime.max.time()))

        # 应用查询条件
        query = query.filter(conditions)

        # 将查询结果序列化为列表
        teams_data = []
        for team in query:
            creator = SpaceUser.objects.filter(space=space, team=team, is_captain=True).first()
            teams_data.append({
                "id": encrypt(team.id),
                "title": team.teamName,
                "demand": team.demand,
                "target_number": team.target_number,
                "current_number": team.members.count(),
                "created_by": creator.realName,
                "created_at": team.created_at.isoformat(),
                "is_recruiting": team.is_recruiting,
            })
        return custom_response(data=teams_data, message="成功获取正在招募队员的队伍列表")

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="竞赛空间不存在", status=404)
    except json.JSONDecodeError:
        return custom_response(message="无效的 JSON 格式", status=400)
    except Exception as e:
        return custom_response(message=f"查询失败：{str(e)}", status=500)

# 获取用户加入的所有队伍
@require_http_methods(["GET"])
def get_user_teams(request):
    try:
        user = request.user0
        created = request.GET.get("created", False)
        # 通过子查询直接获取用户加入的所有队伍
        if created:
            teams = Team.objects.filter(
                created_by=user
            ).distinct()  # 使用 distinct 去重，防止同一个队伍被多次返回
        else:
            teams = Team.objects.filter(
                members__user=user,
            ).distinct()

        team_list = []
        for team in teams:
            # 获取当前队伍的所有成员
            members = SpaceUser.objects.filter(space=team.space,team=team).order_by('-is_captain')
            member_list = [
                {
                    "space_user_id": encrypt(member.id),
                    "user_username":member.user.username,
                    'user_avatar':request.build_absolute_uri(member.user.avatar.url) if member.user.avatar else None,
                    "realName": member.realName,
                    "studentId":member.studentId,
                    "collegeName":member.collegeName,
                }
                for member in members
            ]
            captain = SpaceUser.objects.filter(space=team.space,team=team,is_captain=True).first()
            # 构建队伍信息
            team_info = {
                "space_title": team.space.title,
                "team_id": encrypt(team.id),
                "teamName": team.teamName,
                "team_demand": team.demand,
                "team_target_number": team.target_number,
                "qq": team.qq,
                "team_captain_username": captain.user.username,
                'team_captain_realName': captain.realName,
                "team_captain_avatar": request.build_absolute_uri(captain.user.avatar.url) if captain.user.avatar else None,
                "created_at": team.created_at,
                "is_recruiting": team.is_recruiting,
                "is_locked": team.is_locked,
                "members": member_list  # 包含成员信息
            }
            team_list.append(team_info)

        # 返回统一格式的 JSON 响应
        return custom_response(data=team_list, message="获取成功",status=200)

    except Exception as e:
        # 捕获异常并返回错误信息
        return custom_response(message=f"发生错误：{str(e)}", status=500)

