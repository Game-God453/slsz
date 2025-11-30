from django.conf.urls.static import static
from django.urls import path

from competition_space import views
from slsz import settings

urlpatterns = [
    path("create",views.create_competition_space,name="create_space"),
    path("listSpaces",views.list_competition_spaces,name="list_spaces"),
    path("listSpaceUsers/<str:space_id>",views.list_competition_space_users,name="list_space_users"),
    path("listUserSpaces",views.get_user_competition_spaces,name="list_user_spaces"),
    path("close/<str:space_id>",views.close_competition_space,name="close"),
    path("updateSpace",views.update_competition_space,name="update_space"),
    path("getUserInfo/<str:space_id>",views.get_space_user_info,name="get_space_user_info"),
    path("updateUser",views.edit_space_user_profile,name="edit_space_user"),
    path("addAdmin",views.add_admin_to_competition_space,name="add_admin"),
    path("removeUser",views.remove_user_from_competition_space,name="remove_user"),
    path("getSpaceInfo/<str:space_id>",views.get_space_info,name="get_space_info"),
]