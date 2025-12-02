from django.core.validators import RegexValidator
from django.db import models
from accounts.models import User, School


def poster_path(instance, filename):
    # 这里的 instance 是实际的模型实例
    return f"data/schools/{instance.school.name}/{instance.title}/poster/{filename}"

class CompetitionSpace(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=50,unique=True)
    description = models.TextField(null=True, blank=True)
    poster = models.ImageField(null=True,blank=True, upload_to=poster_path)  # 海报
    category = models.CharField(max_length=50, choices=[
        ('subject', '学科竞赛'),
        ('innovation', '创新创业'),
        ('entertainment', '文娱竞赛'),
        ('others', '其它')
    ])
    level = models.CharField(max_length=20, choices=[
        ('school', '校级'),
        ('province', '省级'),
        ('national', '国家级')
    ])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_competitions')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = u'competition_space'


from teams.models import Team

class SpaceUser(models.Model):
    space = models.ForeignKey(CompetitionSpace, on_delete=models.CASCADE, related_name='space')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='space_user')
    realName = models.CharField(max_length=30, null=True, blank=True)
    studentId = models.CharField(max_length=30, null=True, blank=True)
    collegeName = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', '男'),
        ('female', '女'),
    ], default='male')
    phoneNumber = models.CharField(
        null=True,
        blank=True,
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',  # 正则表达式：11 位数字
                message="手机号码必须是 11 位数字"
            )
        ]
    )
    email = models.EmailField(max_length=30, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='members', null=True,blank=True)
    is_captain = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = u'space_user'
        unique_together = ("space", "user")  # 确保用户对是唯一的

    def __str__(self):
        return f"{self.realName}"

