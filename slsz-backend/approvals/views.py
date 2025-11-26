import json
from datetime import datetime

from django.db.models import Q, Case, When, Exists, OuterRef, IntegerField
from django.views.decorators.http import require_http_methods

from accounts.models import Notify
from competition_space.models import SpaceUser
from teams.models import Team
from utils import custom_response, decrypt, encrypt, send_email_prompt
from .form import SpaceMembershipRequestFilterForm, TeamMembershipRequestFilterForm
from .models import SpaceMembershipRequest, CompetitionSpace, TeamMembershipRequest


@require_http_methods(['POST'])
def submit_spaceMember_request(request):
    try:
        space_id = int(decrypt(request.POST.get('space_id')))
        real_name = request.POST.get('real_name')
        student_id = request.POST.get('student_id')
        college_name = request.POST.get('college_name')

        space = CompetitionSpace.objects.filter(id=space_id).first()
        if not space:
            return custom_response(message="竞赛空间不存在", status=404)

        # 检查用户是否已经提交过申请competition_report
        existing_request = SpaceMembershipRequest.objects.filter(
            space=space, user=request.user0
        ).first()
        if existing_request:
            if existing_request.status == "pending":
                return custom_response(message="您已经提交过申请，请等待管理员处理", status=200)
            elif existing_request.status == "approved":
                return custom_response(message="该申请已通过，不要重新申请", status=200)

        if SpaceUser.objects.filter(space=space, user=request.user0).exists():
            return custom_response(message="已加入该竞赛空间",status=403)

        # 创建新的申请
        smr = SpaceMembershipRequest.objects.create(
            space=space,
            user=request.user0,
            realName=real_name,
            studentId=student_id,
            collegeName=college_name,
        )
        return custom_response(message="申请已成功发送", status=200)

    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(['POST'])
def handle_spaceMember_request(request):
    try:
        if request.user0.role != 'competition_admin':
            return custom_response(message="没有权限", status=403)

        smr_id = int(decrypt(request.POST.get('smr_id')))
        smr = SpaceMembershipRequest.objects.filter(id=smr_id).first()
        if not smr:
            return custom_response(message="该申请单不存在", status=404)

        if smr.status != "pending":
            return custom_response(message="已处理过该申请",status=404)

        action = request.POST.get('action')
        if action == 'approve':
            smr.status = 'approved'
            # 加入竞赛空间用户组
            SpaceUser.objects.get_or_create(user=smr.user, space=smr.space, realName=smr.realName,
                                            collegeName=smr.collegeName, studentId=smr.studentId,email=smr.user.email,
                                            phoneNumber=smr.user.phone,gender=smr.user.gender)
            smr.need_to_notify = True

            if Notify.objects.get(user=smr.user).space_handel_notify:
                send_email_prompt(email_list=[smr.user.email],subject=f"竞赛空间:{smr.space.title}的加入申请结果"
                                  ,message=f"您于时刻：{smr.requested_at}，对于加入竞赛空间：{smr.space.title}的申请已通过。")

            smr.save()
            return custom_response(message="通过申请成功", status=200)
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason')

            smr.status = 'rejected'
            smr.rejection_reason = rejection_reason
            smr.need_to_notify = True

            if Notify.objects.get(user=smr.user).space_handel_notify:
                send_email_prompt(email_list=[smr.user.email],subject=f"竞赛空间:{smr.space.title}的加入申请结果"
                                  ,message=f"您于时刻：{smr.requested_at}，对于加入竞赛空间：{smr.space.title}的申请已被拒绝。\n原因如下：{rejection_reason}")

            smr.save()
            return custom_response(message="拒绝申请成功", status=200)
        else:
            return custom_response(message="无效操作", status=400)

    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["POST"])
def list_space_membership_requests(request):
    try:
        # 解析前端传入的 JSON 数据
        data = json.loads(request.body)

        # 使用表单验证和清洗数据
        form = SpaceMembershipRequestFilterForm(data)
        if not form.is_valid():
            return custom_response(message="无效的筛选条件", status=400)

        # 获取清洗后的数据
        cleaned_data = form.cleaned_data
        space_id = None
        if cleaned_data.get('space_id'):
            space_id = int(decrypt(cleaned_data.get('space_id')))
            space = CompetitionSpace.objects.filter(id=space_id).first()
            if not SpaceUser.objects.filter(space=space, user=request.user0).first().is_admin:
                return custom_response(message="没有获取权限", status=403)
        status = cleaned_data.get('status')
        requested_at_start = cleaned_data.get('requested_at_start')
        requested_at_end = cleaned_data.get('requested_at_end')
        # 构建查询条件
        query = SpaceMembershipRequest.objects.all().order_by(  # 筛选：用户是该请求对应竞赛空间的管理员
            Case(
                When(status='pending', then=1),
                When(status='approved', then=2),
                When(status='rejected', then=3),
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            Exists(
                SpaceUser.objects.filter(
                    space=OuterRef('space'),
                    user=request.user0,
                    is_admin=True
                )
            )
        )
        if not query:
            return custom_response(message="没有申请或不是有效的竞赛空间管理员",status=200)

        conditions = Q()
        if space_id:
            conditions &= Q(space_id=space_id)
        if status:
            conditions &= Q(status=status)
        if requested_at_start:
            conditions &= Q(requested_at__gte=datetime.combine(requested_at_start, datetime.min.time()))
        if requested_at_end:
            conditions &= Q(requested_at__lte=datetime.combine(requested_at_end, datetime.max.time()))

        # 应用查询条件
        query = query.filter(conditions)

        # 将查询结果序列化为列表
        requests_data = [
            {
                "req_id": encrypt(req.id),
                "space_title": req.space.title,
                "realName": req.realName,
                "studentId": req.studentId,
                "collegeName": req.collegeName,
                "user_avatar": request.build_absolute_uri(req.user.avatar.url) if req.user.avatar else None,
                "status": req.status,
                "rejection_reason": req.rejection_reason,
                "requested_at": req.requested_at.isoformat()
            }
            for req in query
        ]

        return custom_response(data=requests_data, message="成功获取竞赛空间申请列表", status=200)

    except json.JSONDecodeError:
        return custom_response(message="无效的 JSON 格式", status=400)
    except Exception as e:
        return custom_response(message=f"查询失败：{str(e)}", status=500)


@require_http_methods(['POST'])
def submit_teamMember_request(request):
    try:
        team_id = int(decrypt(request.POST.get('team_id')))
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return custom_response(message="队伍不存在", status=404)

        if SpaceUser.objects.get(space=team.space, user=request.user0).team:
            return custom_response(message="已经加入该竞赛下的一个队伍，请先退出队伍再申请", status=403)

        request_detail = request.POST.get('request_detail')

        # 检查用户是否已经提交过申请
        existing_request = TeamMembershipRequest.objects.filter(
            team=team, user=request.user0, status='pending'
        ).first()
        if existing_request:
            return custom_response(message="您已经提交过申请，请等待队长处理", status=200)


        # 创建新的申请
        tmr = TeamMembershipRequest.objects.create(
            team=team,
            user=request.user0,
            status='pending',
            request_detail=request_detail,
        )
        return custom_response(message="申请已成功发送", status=200)
    except SpaceUser.DoesNotExist:
        return custom_response(message="该竞赛空间用户不存在", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(['POST'])
def handle_teamMember_request(request):
    try:
        tmr_id = int(decrypt(request.POST.get('tmr_id')))
        tmr = TeamMembershipRequest.objects.filter(id=tmr_id).first()
        if not tmr:
            return custom_response(message="该申请单不存在", status=404)

        if not SpaceUser.objects.filter(space=tmr.team.space, user=request.user0).first().is_captain:
            return custom_response(message="没有权限", status=403)

        if tmr.status != 'pending':
            return custom_response(message="该申请已处理过", status=404)

        action = request.POST.get('action')
        if action == 'approve':
            tmr.status = 'approved'
            # 加入队伍
            space_user = SpaceUser.objects.filter(space=tmr.team.space,user=tmr.user).first()
            space_user.team = tmr.team
            space_user.save()

            tmr.need_to_notify = True

            if Notify.objects.get(user=tmr.user).team_handel_notify:
                send_email_prompt(email_list=[tmr.user.email],subject=f"队伍:{tmr.team.teamName}的组队申请结果"
                                  ,message=f"您于时刻：{tmr.requested_at}，对于加入队伍：{tmr.team.teamName}的申请已通过。")

            tmr.save()
            return custom_response(message="通过申请成功", status=200)
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason')
            tmr.status = 'rejected'
            tmr.rejection_reason = rejection_reason
            tmr.need_to_notify = True

            if Notify.objects.get(user=tmr.user).team_handel_notify:
                send_email_prompt(email_list=[tmr.user.email],subject=f"队伍:{tmr.team.teamName}的组队申请结果"
                                  ,message=f"您于时刻：{tmr.requested_at}，对于加入队伍：{tmr.team.teamName}的申请已被拒绝。\n原因如下：{rejection_reason}")

            tmr.save()
            return custom_response(message="拒绝申请成功", status=200)
        else:
            return custom_response(message="无效操作", status=400)

    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["POST"])
def list_team_membership_requests(request):
    try:
        # 解析前端传入的 JSON 数据
        data = json.loads(request.body)

        # 使用表单验证和清洗数据
        form = TeamMembershipRequestFilterForm(data)
        if not form.is_valid():
            return custom_response(message="无效的筛选条件", status=400)

        # 获取清洗后的数据
        cleaned_data = form.cleaned_data
        team_id = None
        if cleaned_data.get('team_id'):
            team_id = int(decrypt(cleaned_data.get('team_id')))
            team = Team.objects.get(id=team_id)
            if team.created_by != request.user0:
                return custom_response(message="没有获取权限", status=403)
        status = cleaned_data.get('status')
        requested_at_start = cleaned_data.get('requested_at_start')
        requested_at_end = cleaned_data.get('requested_at_end')
        # 构建查询条件

        query = TeamMembershipRequest.objects.all().order_by(
            Case(
                When(status='pending', then=1),
                When(status='approved', then=2),
                When(status='rejected', then=3),
                default=4,
                output_field=IntegerField()
            )
        ).filter(
            team__created_by=request.user0  # 筛选：队伍的创建者是当前用户
        )

        conditions = Q()
        if team_id:
            conditions &= Q(team_id=team_id)
        if status:
            conditions &= Q(status=status)
        if requested_at_start:
            conditions &= Q(requested_at__gte=datetime.combine(requested_at_start, datetime.min.time()))
        if requested_at_end:
            conditions &= Q(requested_at__lte=datetime.combine(requested_at_end, datetime.max.time()))

        # 应用查询条件
        query = query.filter(conditions)

        # 将查询结果序列化为列表
        requests_data = [
            {
                "req_id": encrypt(req.id),
                "team_title": req.team.teamName,
                "user_avatar": request.build_absolute_uri(req.user.avatar.url) if req.user.avatar else None,
                "user_username": req.user.username,
                "request_detail": req.request_detail,
                "status": req.status,
                "rejection_reason": req.rejection_reason,
                "requested_at": req.requested_at.isoformat()
            }
            for req in query
        ]
        return custom_response(data=requests_data, message="成功获取组队申请列表", status=200)

    except Team.DoesNotExist as e:
        return custom_response(message="筛选条件中的队伍不存在", status=400)
    except json.JSONDecodeError:
        return custom_response(message="无效的 JSON 格式", status=400)
    except Exception as e:
        return custom_response(message=f"查询失败：{str(e)}", status=500)


@require_http_methods(["GET"])
def space_membership_requests_feedback(request):
    try:
        # 获取所有 need_to_notify 为 True 的竞赛空间申请单
        space_requests = (SpaceMembershipRequest.objects.filter(user=request.user0,need_to_notify=True)
                          .order_by('-requested_at'))

        requests_data = []
        for req in space_requests:
            requests_data.append({
                "space_title": req.space.title,
                "status": req.status,
                "rejection_reason": req.rejection_reason,
                "requested_at": req.requested_at.isoformat(),
            })
            req.need_to_notify = False
            req.save()

        return custom_response(data=requests_data, message="成功获取竞赛空间申请单的处理结果", status=200)

    except Exception as e:
        return custom_response(message=f"获取竞赛空间进入申请的反馈结果失败：{str(e)}", status=500)


@require_http_methods(["GET"])
def team_membership_requests_feedback(request):
    try:
        # 获取所有 need_to_notify 为 True 的组队申请单
        team_requests = (TeamMembershipRequest.objects.filter(user=request.user0,need_to_notify=True)
                         .order_by('-requested_at'))

        requests_data = []
        for req in team_requests:
            requests_data.append({
                "space_title": req.team.space.title,
                'team_title': req.team.teamName,
                "status": req.status,
                "rejection_reason": req.rejection_reason,
                "requested_at": req.requested_at.isoformat(),
            })
            req.need_to_notify = False
            req.save()

        return custom_response(data=requests_data, message="成功获取组队申请单的处理结果", status=200)

    except Exception as e:
        return custom_response(message=f"获取失败：{str(e)}", status=500)
