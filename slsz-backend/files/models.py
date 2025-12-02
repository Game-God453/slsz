from django.db import models
from accounts.models import User
from competition_space.models import CompetitionSpace

def upload_path(instance, filename):
    # 这里的 instance 是实际的模型实例
    return f"data/schools/{instance.space.school.name}/{instance.space.title}/uploadFiles/{filename}"


class CompetitionFile(models.Model):
    space = models.ForeignKey(CompetitionSpace, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_path)  # 暂时先这样,采用回调函数动态生成路径
    description = models.CharField(max_length=200, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.space.title}"

    class Meta:
        db_table = 'competition_files'
