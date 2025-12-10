import datetime
import json
import os
import random
import uuid

import jwt
import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection
from dotenv import load_dotenv
from jwt import ExpiredSignatureError
from django.conf import settings
from django.http import JsonResponse
from oss2.credentials import EnvironmentVariableCredentialsProvider

load_dotenv()  # 加载.env文件

# *************************************JWTToken加解密***********************************************

class JWTToken:
    _secretKey = os.getenv('JWT_SECRET_KEY')

    def __init__(self, userid, role):
        exp = datetime.datetime.now() + datetime.timedelta(seconds=getattr(settings, "TOKEN_TTL", 60))  # 默认1分钟

        self.payload = {'userID': userid, "role": role, 'exp': exp.timestamp()}

    def encode(self):
        token = jwt.encode(self.payload, self._secretKey, algorithm="HS256")

        return token

    @classmethod
    def decode(cls, token):

        try:
            # 解码并验证 Token
            # algorithms 参数必须与生成 Token 时使用的算法一致
            decoded_payload = jwt.decode(token, cls._secretKey, algorithms=["HS256"], verify_expiration=True)

            return decoded_payload, "登录验证成功"
        except ExpiredSignatureError:
            print("Token 已过期！")
            return None, "登录已过期！"

        except jwt.InvalidTokenError:
            print("Token 无效！")
            return None, "token无效！"

        except Exception as e:
            print(f"其他错误：{e}")
            return None, e

# *************************************统一json回复***********************************************

def custom_response(data=None, message="", status=200):

    response_data = {
        "data": data,
        "message": message
    }
    return JsonResponse(response_data, status=status)

# *************************************数据加密***********************************************

import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

# 使用 SECRET_KEY 生成一个 Fernet 密钥
def generate_fernet_key(secret_key):
    # 使用 hashlib 对 SECRET_KEY 进行哈希处理，确保密钥长度符合要求
    hashed_key = hashlib.sha256(secret_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(hashed_key)
    return fernet_key

# 初始化 Fernet 对象
fernet_key = generate_fernet_key(settings.SECRET_KEY)
cipher_suite = Fernet(fernet_key)

# 加密
def encrypt(elem):
    elem_bytes = str(elem).encode('utf-8')
    encrypted_elem = cipher_suite.encrypt(elem_bytes)
    return encrypted_elem.decode('utf-8')

# 解密
def decrypt(encrypted_elem):
    encrypted_elem_bytes = encrypted_elem.encode('utf-8')
    decrypted_elem = cipher_suite.decrypt(encrypted_elem_bytes)
    return decrypted_elem.decode('utf-8')

# *************************************短信验证码********************************************
def generate_verification_code():
    code = random.randint(100000, 999999)  # 生成一个四位数的验证码
    return str(code)

def aliyun_dysmsapi(phone_number,code):
    ACCESS_KEY_ID = os.getenv('DYSMSAPI_ACCESS_KEY_ID')
    ACCESS_KEY_SECRET = os.getenv('DYSMSAPI_ACCESS_KEY_SECRET')
    REGION = os.getenv('DYSMSAPI_REGION')
    PRODUCT_NAME = os.getenv('DYSMSAPI_PRODUCT_NAME')
    DOMAIN = os.getenv('DYSMSAPI_DOMAIN')

    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)

    sign_name = os.getenv("DYSMSAPI_SIGN_NAME")  # 在阿里云控制台中创建的签名名称
    template_code = os.getenv("DYSMSAPI_TEMPLATE_CODE")  # 在阿里云控制台中创建的模板 CODE
    template_param = json.dumps({'code': code})  # 模板变量参数

    business_id = uuid.uuid1()
    sms_request = SendSmsRequest.SendSmsRequest()
    sms_request.set_TemplateCode(template_code)
    sms_request.set_TemplateParam(template_param)
    sms_request.set_OutId(business_id)
    sms_request.set_SignName(sign_name)
    sms_request.set_PhoneNumbers(phone_number)

    try:
        response = acs_client.do_action_with_exception(sms_request)
        return json.loads(response.decode('utf-8'))
    except Exception as e:
        return str(e)


def verify_code(phone_number, user_code):
    redis_client = get_redis_connection('default')  # 获取 Redis 连接
    saved_code = redis_client.get(phone_number)  # 从 Redis 中获取验证码
    if saved_code is None:
        return False  # 验证码过期或不存在
    return saved_code.decode('utf-8') == user_code  # 验证用户输入的验证码是否正确


# ***********************************************发送邮箱提示***************************************************
def send_email_prompt(email_list,subject,message):
    try:
        send_mail(subject=subject,message=message,recipient_list=email_list,from_email=None)
    except Exception as e:
        raise e


# *************************************文件上传***********************************************

# auth = oss2.ProviderAuthV4(EnvironmentVariableCredentialsProvider())
# # 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为 https://oss-cn-hangzhou.aliyuncs.com。
# endpoint = os.getenv("ENDPOINT")
# # 填写Endpoint对应的Region信息，例如cn-hangzhou。注意，v4签名下，必须填写该参数
# region = os.getenv("REGION")
# # yourBucketName填写存储空间名称。
# bucket_name = os.getenv("BUCKET_NAME")  # 替换为你的Bucket名称
# bucket = oss2.Bucket(auth, endpoint, bucket_name, region=region)
# def generate_unique_filename(original_filename):
#     """
#     生成唯一的文件名，保留原始文件的扩展名。
#     :param original_filename: 原始文件名
#     :return: 唯一的文件名
#     """
#     # 获取文件的扩展名
#     _, file_extension = os.path.splitext(original_filename)
#
#     # 生成 UUID 作为文件名，并拼接扩展名
#     unique_filename = f"{uuid.uuid4()}{file_extension}"
#     return unique_filename
#
# @csrf_exempt  # 如果前端和后端不在同一域名下，可能需要禁用CSRF保护
# def upload_image(request):
#     try:
#         file = request.FILES.get("avatar")
#         if not file:
#             return None
#
#         # 获取文件名并构造OSS中的Object名称
#         object_name = generate_unique_filename(file.name)  # 可以根据需要修改Object名称
#         # print(f"Uploading file: {object_name}")
#
#         result = bucket.put_object(object_name, file)
#         # print('http status: {0}'.format(result.status))
#         # print('request_id: {0}'.format(result.request_id))
#         # print('ETag: {0}'.format(result.etag))
#         # print('date: {0}'.format(result.headers['date']))
#
#         # 返回上传成功的url
#         url = f"https://{bucket_name}.{endpoint[endpoint.rfind('/') + 1:]}/{object_name}"
#         user=request.user0
#         user.avatar=url
#         user.save()
#         return url
#
#     except Exception as e:
#         raise e

