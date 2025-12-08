"""
URL configuration for slsz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


from slsz import settings

admin.site.site_header = '赛链速组后台管理'
admin.site.site_title = '后台管理'
admin.site.index_title = '赛链速组'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/',include("accounts.urls")),
    path('space/',include("competition_space.urls")),
    path('approval/',include("approvals.urls")),
    path('discussion/',include("discussion.urls")),
    path('announcement/',include("announcement.urls")),
    path('files/',include("files.urls")),
    path('team/',include("teams.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)