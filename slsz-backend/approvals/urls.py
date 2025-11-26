from django.urls import path

from approvals import views

urlpatterns = [
    path("submitSpaceRequest", views.submit_spaceMember_request, name="submit_space_request"),
    path("submitTeamRequest",views.submit_teamMember_request, name="submit_team_request"),
    path("handleSpaceRequest",views.handle_spaceMember_request,name="handle_spaceMember_request"),
    path("handleTeamRequest",views.handle_teamMember_request, name="handle_teamMember_request"),
    path("listSpaceRequest",views.list_space_membership_requests,name="list_space_membership_requests"),
    path("listTeamRequest",views.list_team_membership_requests,name="list_team_membership_requests"),
    path("spaceRequestFeedback",views.space_membership_requests_feedback,name="space_membership_requests_feedback"),
    path("teamRequestFeedback",views.team_membership_requests_feedback,name="team_membership_requests_feedback"),
]