from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator
from django.db import models

class School(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'schools'

def avatar_path(instance, filename):
    # 这里的 instance 是实际的模型实例
    return f"data/schools/{instance.school.name}/user/avatar/{filename}"


class UserManager(models.Manager):

    def create_user(self,  phone, username, email=None, password=None, role='student', school=None):
        if not password:
            password = "123456"
        if not school:
            school = School.objects.filter(id=1).first()

        if not phone:
            raise ValueError("Users must have a phone number")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            email=email,
            phone=phone,
            username=username,
            school=school,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_platform_admin(self, phone, username, email=None, password=None):
        user = self.create_user(
            email=email,
            phone=phone,
            username=username,
            password=password,
            role='platform_admin',
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    email = models.EmailField(unique=True,null=True,blank=True)
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',  # 正则表达式：11 位数字
                message="手机号码必须是 11 位数字"
            )
        ]
    )
    gender = models.CharField(max_length=10, choices=[
        ('male', '男'),
        ('female', '女'),
    ], default='male')
    username = models.CharField(max_length=25,null=True,blank=True)
    avatar = models.ImageField(null=True,blank=True,upload_to=avatar_path)
    # password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=[
        ('platform_admin', '平台管理员'),
        ('school_super_admin', '学校超级管理员'),
        ('competition_admin', '竞赛负责人'),
        ('student', '普通学生')
    ], default='student')
    # last_login = models.DateTimeField(null=True)
    # is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    first_name = None
    last_name = None

    USERNAME_FIELD = 'phone'
    # REQUIRED_FIELDS = ['username']  # 添加 REQUIRED_FIELDS 属性

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username if self.username else str(self.id)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def has_perm(self, perm, obj=None):
        # 这里可以根据你的业务逻辑实现权限检查
        # 例如，超级用户有所有权限
        return self.is_staff

    def has_module_perms(self, app_label):
        # 这里可以根据你的业务逻辑实现模块权限检查
        # 例如，工作人员可以访问所有模块
        return self.is_staff

class Notify(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='notify')
    team_handel_notify = models.BooleanField(default=False)
    space_handel_notify = models.BooleanField(default=False)
    announcement_notify = models.BooleanField(default=False)
    reply_notify = models.BooleanField(default=False)
