from django.urls import path

from accounts import views

urlpatterns = [
    path("school",views.SchoolList,name="school"),
    path("sendVerificationCode",views.send_verification_code,name="sendVerificationCode"),
    path("register",views.register,name="register"),
    path("login",views.login,name="login"),
    path("logout",views.logout,name="logout"),
    path("close", views.closeAccount, name="close"),
    path("userInfo",views.GetUserInfo,name="user_info"),
    path("userUpdate",views.UpdateUserInfo,name="user_update"),
    path("deleteUser",views.DeleteAdminOrStudent,name="delete_user"),
    path("chooseToNotify",views.choose_to_notify,name="choose_to_notify"),
]