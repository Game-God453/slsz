import json
import os

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.storage import default_storage
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django_redis import get_redis_connection

from accounts.form import StrictRegisterForm
from accounts.models import School, User, Notify
from competition_space.models import SpaceUser
from slsz.settings import STRONG_REGISTER_VERIFY
from utils import custom_response, JWTToken, encrypt, decrypt, generate_verification_code, aliyun_dysmsapi

from django.core.mail import send_mail

@require_http_methods(['GET'])
def SchoolList(request):
    try:
        # 查询所有学校
        schools = School.objects.all()
        # 构造返回数据
        data = [
            {
                'id': school.id,
                'name': school.name
            }
            for school in schools
        ]
        return custom_response(data=data,message="获取学校列表成功",status=200)
    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['POST'])
def send_verification_code(request):
    try:
        if not STRONG_REGISTER_VERIFY:
            return custom_response(message="服务器未配置手机验证码认证环境，请直接注册",data=400)
        phone_number = request.POST.get('phone_number')
        code = generate_verification_code()  # 生成验证码
        response = aliyun_dysmsapi(phone_number, code)
        if response.get('Code') == 'OK':
            # 将验证码存储到 Redis 中
            redis_client = get_redis_connection('default')
            redis_client.setex(phone_number, 300, code)  # 有效期 5 分钟
            return custom_response(message="验证码发送成功",status=200)
        else:
            return custom_response(message="验证码发送失败",status=500)
    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['POST'])
def register(request):
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        username = data.get('username')
        school_id = data.get('school_id')

        if not phone or not password or not confirm_password or not username or not school_id:
            return custom_response(message="手机号、密码、确认密码、昵称和学校ID不能为空",status=400)

        if password != confirm_password:
            return custom_response(message="两次密码不一致",status=400)

        if User.objects.filter(phone=phone).exists():
            return custom_response(message="手机号已存在，请直接登录",status=400)

        if STRONG_REGISTER_VERIFY:
            form = StrictRegisterForm(request.POST)
            if not form.is_valid():
                return custom_response(message=form.errors, status=400)

        school = School.objects.get(id=school_id)

        if not username:
            username = phone

        user = User.objects.create(
            school=school,
            phone=phone,
            password=make_password(password),
            username=username,
            role='student'
        )

        Notify.objects.create(user=user)

        return custom_response(data={"user_id":encrypt(user.id)},message="注册成功，请登录",status=200)
    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['POST'])
def login(request):
    try:
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if not phone or not password:
            return custom_response(message="手机号和密码不能为空",status=400)

        # 查询用户
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return custom_response(message="该用户不存在",status=404)

        # 验证密码
        if check_password(password, user.password):
            user.last_login = timezone.now()
            user.save()
            # 验证此用户是否已经处于登录态（上次token未失效）
            redis_conn = get_redis_connection("default")
            # 如果当前用户已处于登录状态，则删除之前的token，重新登录
            if redis_conn.get(f"token:{user.id}"):
                redis_conn.delete(f"token:{user.id}")

            token = JWTToken(user.id, user.role).encode()
            # 获取缓存时间
            cache_ttl = getattr(settings, "CACHE_TTL", 60)  # 默认值为 1 分钟
            # 设置缓存
            redis_conn.set(f"token:{user.id}", token, ex=cache_ttl)
            return custom_response(data=token,message="登录成功！",status=200)
        else:
            return custom_response(message="手机号或密码错误",status=401)

    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['POST'])
def logout(request):
    try:
        redis_conn = get_redis_connection("default")
        redis_conn.delete(f"token:{request.user0.id}")
        return custom_response(message="退出登录成功",status=200)
    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['DELETE'])
def closeAccount(request):
    try:
        user = request.user0
        redis_conn = get_redis_connection("default")
        redis_conn.delete(f"token:{user.id}")
        if user.avatar:
            old_avatar_path = user.avatar.path
            if default_storage.exists(old_avatar_path):
                default_storage.delete(old_avatar_path)
        user.delete()
        return custom_response(message="账户注销成功",status=200)

    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['GET'])
def GetUserInfo(request):
    try:
        user = request.user0

        # 获取用户加入的竞赛空间数目
        competition_space_count = SpaceUser.objects.filter(user=user).values('space').distinct().count()

        # 获取用户加入的队伍数目
        team_count = SpaceUser.objects.filter(user=user, team__isnull=False).values('team').distinct().count()

        data = {
            "school": user.school.name,
            "username": user.username,
            "phone": user.phone,
            "email": user.email,
            "role": user.role,
            "avatar": request.build_absolute_uri(user.avatar.url) if user.avatar else None,
            "space_count": competition_space_count,
            "team_count": team_count,
            "is_verified": user.is_verified,
        }
        return custom_response(data=data, message="用户信息获取成功", status=200)
    except Exception as e:
        return custom_response(message=str(e),status=500)

@require_http_methods(['POST'])
def UpdateUserInfo(request):
    try:
        user = request.user0
        user.username = request.POST.get('username',user.username)
        user.email = request.POST.get('email',user.email)

        gender = request.POST.get('gender')
        if gender and (gender != "男" and gender !="女"):
            return custom_response(message="性别只能是男或女",status=400)
        if gender=="男":
            gender="male"
        elif gender=="女":
            gender="female"
        user.gender = gender if gender else user.gender

        avatar = request.FILES.get("avatar")
        if avatar:
            if user.avatar:
                old_avatar_path = user.avatar.path
                if default_storage.exists(old_avatar_path):
                    default_storage.delete(old_avatar_path)
            user.avatar = avatar

        user.save()

        return custom_response(message="用户信息更新成功",status=200)

    except Exception as e:
        return custom_response(message=str(e),status=500)


@require_http_methods(['POST'])
def DeleteAdminOrStudent(request):
    try:
        if request.user0.role != 'super_admin':
            return custom_response(message="没有权限", status=403)

        target_user_id = int(decrypt(request.POST.get('userID')))
        if not target_user_id:
            return custom_response(message="用户ID不能为空",status=400)

        redis_conn = get_redis_connection("default")
        redis_conn.delete(f"token:{target_user_id}")

        target_user = User.objects.get(id=target_user_id)
        target_user.delete()
        return custom_response(message="删除用户成功", status=200)
    except User.DoesNotExist:
        return custom_response(message="用户不存在", status=404)
    except Exception as e:
        return custom_response(message=str(e),status=500)


@require_http_methods(['POST'])
def choose_to_notify(request):
    try:
        data = json.loads(request.body)
        team_handel_notify = data.get('team_handel_notify',False)
        space_handel_notify = data.get('space_handel_notify',False)
        announcement_notify = data.get('announcement_notify',False)
        reply_notify = data.get('reply_notify',False)

        notify = Notify.objects.get(user=request.user0)

        if (team_handel_notify or space_handel_notify or announcement_notify or reply_notify) and not request.user0.email:
            return custom_response(message="请先更新用户的email信息！",status=400)

        notify.team_handel_notify = team_handel_notify
        notify.space_handel_notify = space_handel_notify
        notify.announcement_notify = announcement_notify
        notify.reply_notify = reply_notify
        notify.save()
        return custom_response(message="选择成功",status=200)
    except Notify.DoesNotExist:
        return custom_response(message="通知表不存在",status=400)
    except Exception as e:
        return custom_response(message=str(e),status=500)
