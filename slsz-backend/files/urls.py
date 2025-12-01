from django.urls import path

from files import views

urlpatterns = [
    path("upload", views.upload_competition_file, name="upload_competition_file"),
    path("get/<str:space_id>", views.get_competition_file, name="get_competition_file"),
    path("download/<str:file_id>", views.download_competition_file, name="download_competition_file"),
    path("export/<str:space_id>",views.export_locked_teams_report,name="export_locked_teams_report"),
]