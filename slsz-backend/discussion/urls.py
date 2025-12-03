from django.urls import path

from discussion import views

urlpatterns = [
    path("createQuestion", views.create_question, name="create_question"),
    path("updateQuestion", views.update_question, name="update_question"),
    path("deleteQuestion/<str:question_id>", views.delete_question, name="delete_question"),
    path("createReply", views.create_reply, name="create_reply"),
    path("listAll/<str:space_id>",views.get_questions_and_replies, name="get_questions_and_replies"),
    path("listReplyToMe",views.get_replies_to_user, name="get_replies_to_user"),
    path("listReplyToOthers",views.get_user_replies,name="get_user_replies"),
    path("deleteReply/<str:reply_id>", views.delete_reply, name="delete_reply"),
]