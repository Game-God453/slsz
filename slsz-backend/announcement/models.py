from django.db import models
from accounts.models import User
from competition_space.models import CompetitionSpace, SpaceUser


class Announcement(models.Model):
    space = models.ForeignKey(CompetitionSpace, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发布者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "announcement"


class AnnouncementReadRecord(models.Model):
    space_user = models.ForeignKey(SpaceUser, on_delete=models.CASCADE,related_name="announcement_reads")
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.space_user.id} read: {self.announcement.title}"

    class Meta:
        db_table = "announcement_read_record"
        unique_together = ('space_user', 'announcement')  # 确保一个用户对一条公告只能有一个状态

