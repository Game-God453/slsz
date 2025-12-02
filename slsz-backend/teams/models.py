from django.core.validators import RegexValidator
from django.db import models

from accounts.models import User
from competition_space.models import CompetitionSpace


class Team(models.Model):
    space = models.ForeignKey('competition_space.CompetitionSpace', on_delete=models.CASCADE, related_name='teams')
    teamName = models.CharField(max_length=30)  #
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')
    demand = models.TextField(null=True)   # 描述队伍目前需求
    target_number = models.IntegerField(null=True)
    qq = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_recruiting = models.BooleanField(default=True)  # 是否仍在招募队友
    is_locked = models.BooleanField(default=False)  # 是否确认队伍信息（即完成组队）

    class Meta:
        db_table = 'team'
