from django.urls import path

from teams import views

urlpatterns = [
    path("create", views.create_team, name="create_team"),
    path("updateTeam", views.update_team, name="update_team"),
    path("dissolve/<str:team_id>", views.dissolve_team, name="dissolve_team"),
    path("remove",views.remove_member,name="remove_member"),
    path("leave/<str:team_id>", views.leave_team, name="leave_team"),
    path("recruit",views.recruit_or_not,name="recruit_or_not_team"),
    path("lock",views.lock_or_unlock_teamMembers,name="lock_or_unlock_teamMembers"),
    path("listRecruiting",views.list_recruiting_teams,name="list_recruiting_teams"),
    path("getUserTeams",views.get_user_teams,name="get_user_teams"),

]