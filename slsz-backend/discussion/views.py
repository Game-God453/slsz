from django.core.files.storage import default_storage
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from accounts.models import User, Notify
from competition_space.models import CompetitionSpace, SpaceUser
from utils import custom_response, decrypt, encrypt, send_email_prompt
from .form import QuestionForm, QuestionImageForm
from .models import Question, QuestionImage, Reply, ReplyImage


@require_http_methods(["POST"])
def create_question(request):
    try:
        space = CompetitionSpace.objects.get(id=int(decrypt(request.POST.get('space_id'))))
        if not SpaceUser.objects.filter(space=space,user=request.user0).exists():
            return custom_response(message="没有权限", status=404)

        form = QuestionForm(request.POST)
        if not form.is_valid():
            return custom_response(message="无效的表单数据", status=400)

        with transaction.atomic():
            question = form.save(commit=False)  # 不立即保存表单数据（这里是：content）到数据库，而是返回一个模型实例
            question.author = request.user0
            question.space = space
            question.save()
            # 处理图片上传
            if request.FILES:
                for file in request.FILES.getlist('images'):
                    image_form = QuestionImageForm({'question': question.id}, {'image': file})
                    if image_form.is_valid():
                        image_form.save()
                    else:
                        return custom_response(message="无效图片或问题，上传失败", status=400)

        return custom_response(data={"question_id": encrypt(question.id)},message="问题发布成功", status=200)

    except CompetitionSpace.DoesNotExist:
        return custom_response(message="该竞赛空间不存在", status=404)
    except Exception as e:
        return custom_response(message=f"发布失败{str(e)}", status=500)


@require_http_methods(["POST"])
def update_question(request):
    try:
        question = Question.objects.get(id=int(decrypt(request.POST.get('question_id'))))
        if question.author != request.user0:
            return custom_response(message="没有权限修改该问题", status=403)

        form = QuestionForm(request.POST, instance=question)
        if not form.is_valid():
            return custom_response(message="无效的表单数据", status=400)

        form.save()

        # 删除旧图片
        old_question_images = QuestionImage.objects.filter(question=question)
        for q_image in old_question_images:
            path = q_image.image.path
            if default_storage.exists(path):
                default_storage.delete(path)
        old_question_images.delete()

        # 重新上传图片
        if request.FILES:
            for file in request.FILES.getlist('images'):
                image_form = QuestionImageForm({'question': question.id}, {'image': file})
                if image_form.is_valid():
                    image_form.save()
                else:
                    return custom_response(message="无效图片或问题，更新失败", status=400)

        return custom_response(message='问题修改成功', status=200)

    except Question.DoesNotExist:
        return JsonResponse({"message": "问题不存在"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"修改失败：{str(e)}"}, status=500)


@require_http_methods(["DELETE"])
def delete_question(request, question_id):
    try:
        question = Question.objects.get(id=int(decrypt(question_id)))
        if question.author != request.user0:
            return custom_response(message="没有权限删除该问题", status=403)

        # 删除图片
        question_images = QuestionImage.objects.filter(question=question)
        for q_image in question_images:
            path = q_image.image.path
            if default_storage.exists(path):
                default_storage.delete(path)
        question_images.delete()

        question.delete()
        return custom_response(message="问题删除成功", status=200)

    except Question.DoesNotExist:
        return JsonResponse({"message": "问题不存在"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"问题删除失败：{str(e)}"}, status=500)


@require_http_methods(["POST"])
def create_reply(request):
    try:
        question = Question.objects.get(id=int(decrypt(request.POST.get('question_id'))))
        from_user = request.user0
        to_space_user = SpaceUser.objects.get(id=int(decrypt(request.POST.get('to_space_user_id'))))
        content = request.POST.get('content')
        if content == '' or content is None:
            return custom_response(message="无效回复", status=400)

        images = request.FILES.getlist('images')  # 获取多张图片

        with transaction.atomic():
            reply = Reply.objects.create(
                question=question,
                from_user=from_user,
                to_user=to_space_user.user,
                content=content,
                need_to_notify=True
            )
            for image in images:
                ReplyImage.objects.create(reply=reply, image=image)

        if Notify.objects.get(user=to_space_user.user).reply_notify:
            send_email_prompt(email_list=[to_space_user.user.email],subject=f"{question.space.title}问答区消息回复提醒"
                              ,message=f"回复人：{reply.from_user.username}\n内容：{reply.content}\n更多详情请进入网站问答区获取")

        return custom_response(data={"reply_id": encrypt(reply.id)}, message="回复成功",status=200)
    except Question.DoesNotExist:
        return custom_response(message="问题不存在", status=404)
    except User.DoesNotExist:
        return custom_response(message="目标用户不存在", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)


# 获取竞赛空间问答区的所有内容
@require_http_methods(["GET"])
def get_questions_and_replies(request, space_id):
    try:
        space = CompetitionSpace.objects.get(id=int(decrypt(space_id)))
        questions = Question.objects.filter(space=space).order_by('-created_at')

        data = []
        for question in questions:
            question_images = QuestionImage.objects.filter(question=question)
            question_images_urls = [request.build_absolute_uri(q_image.image.url) for q_image in question_images if q_image.image]
            author_space_user = SpaceUser.objects.get(space=space, user=question.author)
            question_data = {
                "question_id": encrypt(question.id),
                "author_space_user_id": encrypt(author_space_user.id),
                "author_username": question.author.username,
                "author_avatar": request.build_absolute_uri(question.author.avatar.url) if question.author.avatar else None,
                "content": question.content,
                "question_images_urls": question_images_urls,
                "created_at": question.created_at,
                "replies": []
            }
            replies = question.replies.all()
            # 管理员对问题提出者的回复排在前面
            admin_replies = [r for r in replies if SpaceUser.objects.get(space=space, user=r.from_user).is_admin
                             and r.to_user == question.author]
            other_replies = [r for r in replies if r not in admin_replies]
            sorted_replies = admin_replies + sorted(other_replies, key=lambda r: r.created_at)
            for reply in sorted_replies:
                reply_images = ReplyImage.objects.filter(reply=reply)
                from_space_user = SpaceUser.objects.get(space=space, user=reply.from_user)
                reply_images_urls = [request.build_absolute_uri(r_image.image.url) for r_image in reply_images if r_image.image]
                reply_data = {
                    "reply_id": encrypt(reply.id),
                    "from_space_user_id": encrypt(from_space_user.id),
                    "from_user": reply.from_user.username,
                    "from_user_avatar": request.build_absolute_uri(from_space_user.user.avatar.url) if from_space_user.user.avatar else None,
                    "to_user": reply.to_user.username,
                    "content": reply.content,
                    "reply_images_urls": reply_images_urls,
                    "created_at": reply.created_at,
                }
                question_data["replies"].append(reply_data)
            data.append(question_data)

        return custom_response(data=data,message="获取竞赛空间问答区内容成功",status=200)
    except CompetitionSpace.DoesNotExist:
        return custom_response(message="竞赛空间不存在", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["GET"])
def get_replies_to_user(request):
    try:
        user = request.user0
        replies = Reply.objects.filter(to_user=user, need_to_notify=True).order_by('question__space', 'question')

        data = []
        space_replies = {}
        count = 0
        for reply in replies:
            space_id = reply.question.space.id
            if space_id not in space_replies:
                space_replies[space_id] = {"space": reply.question.space.title, "questions": {}}

            question_id = reply.question.id
            if question_id not in space_replies[space_id]["questions"]:
                space_replies[space_id]["questions"][question_id] = {
                    "question": reply.question.content,
                    "question_poster": reply.question.author.username,
                    "replies": []
                }
            reply_images = ReplyImage.objects.filter(reply=reply)
            reply_images_urls = [request.build_absolute_uri(r_image.image.url) for r_image in reply_images if r_image.image]
            reply_data = {
                "from_user_avatar": request.build_absolute_uri(reply.from_user.avatar.url) if reply.from_user.avatar else None,
                "from_user_username": reply.from_user.username,
                "content": reply.content,
                "reply_images_urls": reply_images_urls,
                "created_at": reply.created_at
            }
            count += 1
            space_replies[space_id]["questions"][question_id]["replies"].append(reply_data)

        # 更新need_to_notify为False
        replies.update(need_to_notify=False)

        for space_id, space_data in space_replies.items():
            for question_id, question_data in space_data["questions"].items():
                data.append({
                    "space_title": space_data["space"],
                    "question_content": question_data["question"],
                    "question_poster": question_data["question_poster"],
                    "replies": question_data["replies"]
                })

        return custom_response(data={"count": count, "replies": data},message="获取对用户的所有回复成功",status=200)
    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["GET"])
def get_user_replies(request):
    try:
        user = request.user0
        replies = Reply.objects.filter(from_user=user).order_by('question__space', 'question')

        data = []
        space_replies = {}
        for reply in replies:
            space_id = reply.question.space.id
            if space_id not in space_replies:
                space_replies[space_id] = {"space": reply.question.space.title, "questions": {}}

            question_id = reply.question.id
            if question_id not in space_replies[space_id]["questions"]:
                space_replies[space_id]["questions"][question_id] = {
                    "question": reply.question.content,
                    "question_poster": reply.question.author.username,
                    "replies": []
                }

            reply_images = ReplyImage.objects.filter(reply=reply)
            reply_images_urls = [request.build_absolute_uri(r_image.image.url) for r_image in reply_images if r_image.image]
            reply_data = {
                "reply_id": encrypt(reply.id),
                "to_user_username": reply.to_user.username,
                "content": reply.content,
                "reply_images_urls": reply_images_urls,
                "created_at": reply.created_at
            }
            space_replies[space_id]["questions"][question_id]["replies"].append(reply_data)

        for space_id, space_data in space_replies.items():
            for question_id, question_data in space_data["questions"].items():
                data.append({
                    "space_title": space_data["space"],
                    "question_content": question_data["question"],
                    "question_poster": question_data["question_poster"],
                    "replies": question_data["replies"]
                })

        return custom_response(data={"count": len(data), "replies": data},message="获取对其他用户的所有回复成功",status=200)
    except Exception as e:
        return custom_response(message=str(e), status=500)


@require_http_methods(["DELETE"])
def delete_reply(request, reply_id):
    try:
        reply = Reply.objects.get(id=int(decrypt(reply_id)))
        if reply.from_user != request.user0:
            return custom_response(message="无权限删除该回复", status=403)

        # 删除图片
        reply_images = ReplyImage.objects.filter(reply=reply)
        for r_image in reply_images:
            path = r_image.image.path
            if default_storage.exists(path):
                default_storage.delete(path)
        reply_images.delete()

        reply.delete()
        return custom_response(message="回复删除成功",status=200)
    except Reply.DoesNotExist:
        return custom_response(message="回复不存在", status=404)
    except Exception as e:
        return custom_response(message=str(e), status=500)