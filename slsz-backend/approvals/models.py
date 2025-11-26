from django.db import models
from accounts.models import User
from competition_space.models import CompetitionSpace
from teams.models import Team

class SpaceMembershipRequest(models.Model):
    space = models.ForeignKey(CompetitionSpace, on_delete=models.CASCADE, related_name='membership_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competition_requests')
    realName = models.CharField(max_length=30)
    studentId = models.CharField(max_length=30)
    collegeName = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=[
        ('pending', '待处理'),
        ('approved', '通过'),
        ('rejected', '驳回')
    ], default='pending')
    rejection_reason = models.TextField(null=True,blank=True)
    need_to_notify = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"from: {self.user.username if self.user.username else str(self.user.id)} to: {self.space.title}"

    class Meta:
        db_table = 'space_membership_request'

class TeamMembershipRequest(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='membership_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_requests')
    status = models.CharField(max_length=20, choices=[
        ('pending', '待处理'),
        ('approved', '接受'),
        ('rejected', '拒绝')
    ], default='pending')
    request_detail = models.TextField(null=True,blank=True)
    rejection_reason = models.TextField(null=True,blank=True)
    need_to_notify = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'team_membership_request'


