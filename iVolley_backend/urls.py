from django.urls import path
from .views import *

urlpatterns = [
    path("register/", register),  # 测试完成
    path("login/", login),  # 测试完成
    path("logout/", logout),  # 测试完成
    path("get_personal_profile/", get_personal_profile),  # 测试完成
    path("upload_profile/", upload_profile),  # 测试完成
    path("change_password/", change_password),  # 测试完成
    # -------- 通用 ↑ ------ 教师 /学生端 ↓ --------#
    path("storage_video/", storage_video),
    path("storage_img/", storage_img),
    path("stu2videos/", stu2videos),
    path("stu2imgs/", stu2imgs),
    path("get_video_profile/", get_video_profile),
    path("get_img_profile/", get_img_profile),
    path("del_img/", delete_img),
    path("del_video/", delete_video),
    # ---------- 学生端 ↑ ------ 教师端 ↓ ---------#
    path("create_class/", create_class),  # 测试完成
    path("tea2classes/", tea2classes),  # 测试完成
    path("teacher_change_class_name/", teacher_change_class_name),  # 11-28新增
    path("class2students/", class2students),  # 测试完成
    path("tea2students/", tea2students),  # 测试完成
    path("tea2stu2videos/", tea2stu2videos),
    path("tea2stu2imgs/", tea2stu2imgs),
    path("add_student/", add_student),
    path("teacher_add_videofeedback/", teacher_add_videofeedback),
    path("teacher_add_imgfeedback/", teacher_add_imgfeedback),
    path("teacher_add_material/", teacher_add_material),
    # ------------------- 作业端 ---------------------- #
    path("teapub_notice/", teapub_notice),  # 测试完成，记得migrate
    path("teapub_homework/", teapub_homework),  # 测试完成
    path("tea2hw2info/", tea2hw2info),  # 测试完成
    path("tea2hw2profile/", tea2hw2profile),  # 测试完成
    path("stu2hw2info/", stu2hw2info),
    path("stu2hw2profile/", stu2hw2profile),
    path("stu2notice/", stu2notice),
    path("student_read_notice/", student_read_notice),
    path("student_get_material/", student_get_material),
    path("stu_sub_hw/", stu_sub_hw),
    path("database_init/", database_init),
    # -------------------签到---------------------------- #
    path("student_signin/", student_signin),
    path("student_getSignList/", student_getSignList),
    path("teapub_sign/", teapub_sign),
    path("teamodify_sign/", teamodify_sign),
    path("teaget_signprofile/", teaget_signprofile),
    path("teaget_sign/", teaget_sign),
    path("tea_modify_signTime/", tea_modify_signTime),
    path("teaget_stufiles/", teaget_stufiles),

    path("openpose/", openpose),
    path("remote_dispatch/", RemoteDispatch),
    path("task_finish/", TaskFinished),
    path("tea_reset_pwd/", tea_reset_pwd),
    path("wx_login/", wx_login)
    # path("add_semester/", add_semester), 多余功能，直接在创建班级的时候默认创建学期就好
    # path("get_SSC/", get_SSC), 还不知道这个要干啥
    # path("add_tag/", add_tag),
    # path("del_err/", del_err),
    # path("redo/", redo)
]
