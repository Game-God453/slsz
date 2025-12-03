from django import forms
from .models import Question, QuestionImage, Reply, ReplyImage

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['content']

class QuestionImageForm(forms.ModelForm):
    class Meta:
        model = QuestionImage
        fields = ['question', 'image']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']

class ReplyImageForm(forms.ModelForm):
    class Meta:
        model = ReplyImage
        fields = ['reply', 'image']