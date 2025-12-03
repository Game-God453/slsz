from django.db import models
from accounts.models import User
from competition_space.models import CompetitionSpace

def question_image_path(instance, filename):
    # 这里的 instance 是实际的模型实例
    return f"data/schools/{instance.question.space.school.name}/{instance.question.space.title}/question_images/{filename}"

def reply_image_path(instance, filename):
    # 这里的 instance 是实际的模型实例
    return f"data/schools/{instance.reply.question.space.school.name}/{instance.reply.question.space.title}/reply_images/{filename}"

class Question(models.Model):
    space = models.ForeignKey(CompetitionSpace, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question"


class QuestionImage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='q_images')
    image = models.ImageField(upload_to=question_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Question {self.question.id}"


class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='replies')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_reply')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_reply')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    need_to_notify = models.BooleanField(default=False)

    class Meta:
        db_table = "reply"

class ReplyImage(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='r_images')
    image = models.ImageField(upload_to=reply_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)