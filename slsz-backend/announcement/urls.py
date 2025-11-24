from django.urls import path

from announcement import views

urlpatterns = [
    path("create", views.create_announcement, name="create_announcement"),
    path("update", views.update_announcement, name="update_announcement"),
    path("delete/<str:announcement_id>", views.delete_announcement, name="delete_announcement"),
    path("getUnread",views.get_unread_announcement_count, name="get_unread_announcement_count"),
    path("getById/<str:announcement_id>",views.get_announcement_by_id, name="get_announcement_by_id"),
    path("getAll",views.get_user_announcements, name="get_user_announcements"),
    path("markRead/<str:announcement_id>",views.mark_announcement_as_read, name="mark_announcement_as_read"),
]