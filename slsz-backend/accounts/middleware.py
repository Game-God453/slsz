from django.http import JsonResponse
from django.urls import reverse
from django_redis import get_redis_connection
from utils import custom_response, decrypt
from accounts.models import User
from utils import JWTToken

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 定义允许访问的主路由前缀列表
        # self.allowed_prefixes = [
        #     '/account/',  # 主 API 路由
        #     '/admin/',  # Django 管理后台
        #     '/static/',  # 静态文件
        #     '/media/',  # 媒体文件
        # ]

    def __call__(self, request):
        # 检查请求路径是否以任何一个允许的前缀开始
        # if not any(request.path.startswith(prefix) for prefix in self.allowed_prefixes):
        #     # 如果不是允许的前缀，直接返回 403 禁止访问
        #     return custom_response(status=403)

        # 如果是登录或注册，则直接处理请求

        request.user0 = request.user

        if request.path in ['/account/school','/account/login','/account/register']:
            return self.get_response(request)

        if request.path.startswith('/media/'):
            return self.get_response(request)

        if request.path.startswith('/static/'):
            return self.get_response(request)

        if request.path.startswith('/favicon.ico'):
            return self.get_response(request)

        if request.path.startswith('/admin'):
            # request.user0.role = 'platform_admin'
            return self.get_response(request)

   
        # 检查用户是否已经登录
        token = request.headers.get('Authorization')

        payload, error_message = JWTToken.decode(token=token)

        if not payload:
            return custom_response(message=error_message, status=401)

        userid = payload.get('userID')

        user = User.objects.filter(id=userid).first()

        if not user:
            return custom_response(message='当前用户未注册或已注销', status=404)

        request.user0 = user

        redis_conn = get_redis_connection("default")
        stored_token = redis_conn.get(f"token:{userid}")

        if not stored_token or stored_token.decode('utf-8') != token:
            return custom_response(message="请重新登陆", status=401)

        return self.get_response(request)