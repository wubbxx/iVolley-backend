# 1231279381274981274891274981273912387
import base64
import os
import re
import time
from datetime import datetime, timedelta

import pandas as pd
import json

from iVolley_backend.utils import *
import random
from django.contrib.auth import logout as dj_logout, login as dj_login
from django.forms import model_to_dict, CharField, BooleanField
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import quote
from iVolley import settings
from iVolley_backend.models import *
from iVolley_backend.tasks import openpose
import requests
from math import radians, sin, cos, sqrt, atan2


def is_time_difference_within_threshold(time_str1, time_str2, threshold_minutes=5):  # 默认5分钟以内签到
    # 将字符串转换为 datetime 对象
    time_format = "%Y-%m-%d-%H-%M-%S"
    time1 = datetime.strptime(time_str1, time_format)
    time2 = datetime.strptime(time_str2, time_format)
    # 计算两个时间的差值
    time_difference = time1 - time2
    print(time1)
    print(time2)
    print(time_difference)
    # 判断差值是否在阈值内
    return abs(time_difference) <= timedelta(minutes=threshold_minutes)


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = 6371.0
    distance = R * c * 1000
    return distance


def rename_file(fileName):
    base_name, extension = os.path.splitext(fileName)
    fn = time.strftime('%Y-%m-%d-%H-%M-%S')  # 获取当前时间字符串
    new_name = f"{fn}_{base_name}{extension}"
    return new_name


def index(request):
    return render(request, 'index.html')


def test_openid(request):
    openid = request.session.get('openid')
    print(openid)
    return JsonResponse({"open": openid})


def wx_login(request):
    code = request.POST.get('code')
    print(f"code: {code}")
    # 利用code获取access_token
    appid = "wx6251a5ac450a38c0"
    secret = "ca3e34b59dbb72c510b504499afc549a"
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    response = requests.get(url)
    data = response.json()
    print(f"data = {data}")
    session_key = data.get('session_key')
    openid = data.get('openid')
    # url = f'https://api.weixin.qq.com/sns/userinfo?access_token={session_key}&openid={openid}'
    # response = requests.get(url)
    # response.encoding = 'utf-8'  # 设置响应内容的编码为UTF-8
    # user_info = response.json()
    # backend = 'django.contrib.auth.backends.ModelBackend'
    user = User.objects.get(username='21371476')
    dj_login(request, user)  # 登录用户，传入backend参数
    request.session['openid'] = openid
    return JsonResponse({"status": 200})


def get_post_url(init_dir, post_base):
    name = init_dir.rsplit("/")[-1]
    return post_base + name


allow_stu = ["21373267"]
sha256 = 'pbkdf2_sha256$720000$op10xq6pwHqWVtWSyVhluL$AaBnSG2Pr6fJmojAX85wUjpPMyZ7EgBlJiBCW42rKnM='


def get_wx_open_id(code):
    appid = "wx6251a5ac450a38c0"
    secret = "ca3e34b59dbb72c510b504499afc549a"
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'
    response = requests.get(url)
    data = response.json()
    print(f"get wx id {data}")
    return data.get('openid')


# 盛春媛：07363；陆科：06643；黎宇翔：08865；杨昊：09424；王晨：11070

def get_role(id):
    allow_tea = []
    teachers = Teacher.objects.all()
    for teacher in teachers:
        allow_tea.append(teacher.last_name)
    print(allow_tea)
    if id in allow_stu:
        return 0
    elif id in allow_tea:
        print("id in allow tea")
        return 1
    else:
        return -1  # 无权限

invitation_codes = ["1", "2", "3"]
def register(request):
    def regBrandNew(role, open_id, user_id, first_name, school, invitation_code):
        print(role)
        if role == "1":
            if invitation_code in invitation_codes:
                teacher = Teacher.objects.create_user(
                    username=open_id,
                    first_name=first_name,
                    last_name=user_id,
                    is_staff=True,  # 0->学生 1->老师
                    email=school
                )
                return teacher
            return None
        elif role == "0":
            student = Student.objects.create_user(
                username=open_id,
                first_name=first_name,
                last_name=user_id,
                is_staff=False,
                email=school
            )
            return student
        else:
            print("err!!!!")
            return None
    open_id = request.POST.get('openid')
    user_id = request.POST.get('id')
    role = request.POST.get('role')
    first_name = request.POST.get('name')
    school = request.POST.get('school')
    password = request.POST.get('password', None)
    invitation_code = request.POST.get('invitation_code', None)
    print(f"open_id: {open_id}")
    print(f"user_id: {user_id}")
    print(f"role: {role}")
    print(f"first_name: {first_name}")
    print(f"school: {school}")
    print(f"password: {password}")
    print(f"invitation_code: {invitation_code}")
    if school == "0":
        try:
            user = Student.objects.get(username=user_id)
            if user.pwd == password:
                user.username = open_id
                user.save()
                dj_login(request, user)
                request.session['username'] = open_id
                return JsonResponse({"status": 200})
            else:
                if password is None:
                    return JsonResponse({"status": 500})
                return JsonResponse({"status": 400})
        except ObjectDoesNotExist:
            res = regBrandNew(role, open_id, user_id, first_name, school, invitation_code)
            if res is None:
                return JsonResponse({"status": 600})
            return JsonResponse({"status": 300})
    else:
        res = regBrandNew(role, open_id, user_id, first_name, school, invitation_code)
        if res is None:
            return JsonResponse({"status": 600})
        return JsonResponse({"status": 300})

def login(request):
    code = request.POST.get('code')
    openid = get_wx_open_id(code)
    print(f"login - {openid}")
    try:
        user = User.objects.get(username=openid)
        dj_login(request, user)  # 登录用户
        request.session['username'] = openid
        role = "0"
        if user.is_staff:
            role = "1"
        return JsonResponse({"status": 200, "role": role, "openid": openid})
    except ObjectDoesNotExist:
        return JsonResponse({"status": 400, "role": "-1", "openid": openid})


def logout(request):
    dj_logout(request=request)
    response = JsonResponse({
        'status': 200
    })
    return response


def change_password(request): # 没用
    user_id = request.session.get('username')
    user = User.objects.get(username=user_id)
    old_pwd = request.POST.get('old_pwd')
    new_pwd = request.POST.get('new_pwd')
    new_pwd_again = request.POST.get('new_pwd_again')
    print(new_pwd_again)
    print(new_pwd)
    if new_pwd != new_pwd_again:
        return JsonResponse({"status": 400})

    if get_role(user_id) == 1:
        tea = Teacher.objects.get(username=user_id)
        if tea.pwd == old_pwd:
            tea.pwd = new_pwd
            tea.save()
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status": 401})
    else:
        stu = Student.objects.get(username=user_id)
        if stu.pwd == old_pwd:
            stu.pwd = new_pwd
            stu.save()
            return JsonResponse({"status": 200})
        else:
            return JsonResponse({"status": 401})


def upload_profile(request):
    student_id = request.session.get('username')
    user = User.objects.get(username=student_id)
    file = request.FILES.get('URL')
    fn = time.strftime('%Y_%m_%d_%H_%M_%S')  # 重新定义图片名
    img_name = fn + file.name
    dir = settings.POST_IMG_DIR + str(img_name)
    destination = open(dir, 'wb+')
    for chunk in file.chunks():  # 存储图片在本地
        destination.write(chunk)
    destination.close()

    user.last_name = get_post_url(dir, settings.POST_IMG_PATH)
    user.save()
    print(user.last_name)
    return JsonResponse({"status": 200})


@csrf_exempt
def get_personal_profile(request):
    if request.method == "GET":
        return JsonResponse({"status": 400})
    user_id = request.session.get('username')
    res = User.objects.get(username=user_id)
    res_class_name = ""
    res_major = ""
    if res.is_staff == 0:
        stu_class = Student_class.objects.filter(student_ID=res).first()
        res_class_name = stu_class.class_ID.name

    if res is None:
        response = JsonResponse({"status": 400})
    else:
        response = JsonResponse({
            'status': 200,
            'profile': {
                'user_id': res.last_name,
                'name': res.first_name,
                'class_name': res_class_name,
                'major': res_major,
                'role': 1 if res.is_staff is True else 0,
                'URL': "https://ivolley.cn:8443/post_img/teacher.jpg",
            }
        })
    return response


def check_file(my_file, allow_types, size_limit):
    suffix = my_file.name.rsplit(".")[-1].lower()  # 将后缀转换为小写
    correct_type = suffix in allow_types
    if not correct_type:
        return 1  # 文件类型不正确
    file_size_mb = my_file.size / 1024 / 1024
    if file_size_mb > size_limit:
        return 2  # 文件大小超过限制
    return 0  # 文件类型和大小都符合要求


def storage_video(request):
    if request.method != "POST":
        return JsonResponse({"status": 400, "error": "请求错误"})
    student_id = request.session.get('username')
    student = Student.objects.get(username=student_id)
    tag = int(request.POST.get('tag'))
    homework_id = int(request.POST.get('homework_id'))
    homework = Homework.objects.get(ID=homework_id)
    print(homework_id)
    print(homework)
    print(homework.ID)
    videoFile = request.FILES.get("video")
    allow_types = homework.type_limit.split('_')
    allow_types = ['asf', 'avi', 'gif', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'ts', 'wmv']

    check = check_file(videoFile, allow_types, 20)
    if check == 1:
        return JsonResponse({"status": 400})
    elif check == 2:
        return JsonResponse({"status": 401})
    # 重新定义视频名
    suffix = videoFile.name.split('.')[-1]
    init_name = f"{student.first_name}-{student.last_name}-{(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}.{suffix}"
    video_name = f"{student.last_name}_{(datetime.now() + timedelta(hours=8)).strftime('%Y_%m_%d_%H_%M_%S')}.{suffix}"
    # 存储图片在服务器本地
    dir = settings.POST_VIDEO_DIR + video_name
    destination = open(dir, 'wb+')
    for chunk in videoFile.chunks():
        destination.write(chunk)
    destination.close()
    # 写数据库
    video = Video.objects.create(
        student_ID=student,
        homework_ID=homework,
        URL=dir,
        AI_status=False,
        tag=tag,
        AI_feedback="未检测完成或检测失败！",
        init_name=init_name
    )
    if homework_id == 1:  # 自主练习
        for teacher in Teacher.objects.all():
            TeacherRVideo.objects.create(
                teacher_ID=teacher,
                video_ID=video,
                read="0"
            )
    else:
        classe = homework.class_ID
        teacher = Teacher.objects.get(username=classe.teacher_ID)
        TeacherRVideo.objects.create(
            teacher_ID=teacher,
            video_ID=video,
            read="0"
        )
    # openpose.delay(video.ID, dir, 0, tag)  # AI异步执行任务
    return JsonResponse({"status": 200})


def storage_img(request):
    if request.method != "POST":
        return JsonResponse({"status": 400, "error": "请求错误"})

    user_id = request.session.get('username')
    student = Student.objects.get(username=user_id)
    homework_id = int(request.POST.get('homework_id'))
    homework = Homework.objects.get(ID=homework_id)
    tag = request.POST.get('tag')
    imageFile = request.FILES.get("img")
    allow_types = homework.type_limit.split('_')
    allow_types = ['bmp', 'dng', 'jpeg', 'jpg', 'mpo', 'png', 'tif', 'tiff', 'webp', 'pfm']
    check = check_file(imageFile, allow_types, 20)
    if check == 1:
        print("status: 400")
        return JsonResponse({"status": 400})  # 文件类型不正确
    elif check == 2:
        print("status: 401")
        return JsonResponse({"status": 401})  # 文件大小超出限制
    print(imageFile)
    suffix = imageFile.name.split('.')[-1]
    img_name = f"{student.first_name}-{student.last_name}-{(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d_%H_%M_%S')}.{suffix}"
    # img_name = f"{user_id}_{(datetime.now() + timedelta(hours=8)).strftime('%Y_%m_%d_%H_%M_%S')}.{suffix}"
    dir = settings.POST_IMG_DIR + img_name
    destination = open(dir, 'wb+')
    for chunk in imageFile.chunks():  # 存储图片在本地
        destination.write(chunk)
    destination.close()
    print("????")
    print(f"homework.ID{homework.ID}")
    image = Image.objects.create(  # 写数据库
        student_ID=student,
        homework_ID=homework,
        URL=dir,
        AI_status=False,
        tag=tag
    )
    if homework_id == 1:  # 自主练习
        for teacher in Teacher.objects.all():
            TeacherRImage.objects.create(
                teacher_ID=teacher,
                image_ID=image,
                read="0"
            )
    else:
        classe = homework.class_ID
        teacher = Teacher.objects.get(username=classe.teacher_ID)
        TeacherRImage.objects.create(
            teacher_ID=teacher,
            image_ID=image,
            read="0"
        )
    # openpose.delay(image.ID, dir, 1, tag)  # AI异步执行任务
    return JsonResponse({"status": 200})


def stu2videos(request):
    student_id = request.session.get('username')
    stu = Student.objects.get(username=student_id)
    video_list = []
    videos = Video.objects.filter(student_ID=stu, homework_ID=1).all()
    for video in videos:
        video_id = video.ID
        subtime = video.post_time
        name = video.URL.rsplit("/")[-1]
        URL = settings.POST_VIDEO_PATH + name
        print(f"name:{name}")
        if video.AI_status == True:
            AI_status = 1
            AI_feedback = video.AI_feedback
            if video.error_video != None:
                error_video = settings.ERROR_VIDEO_PATH + video.error_video.rsplit("/")[-1]
            else:
                error_video = None
        else:
            AI_status = 0
            AI_feedback = None
            error_video = None
        tea_feedback = VidFeedback.objects.filter(video_ID=video_id).all()
        if tea_feedback.count() != 0:
            teacher_status = 1
            teacher_feedback = tea_feedback.first().content
            type_str = tea_feedback.first().type
        else:
            teacher_status = 0
            teacher_feedback = None
            type_str = "无"
        print(f"err:{error_video}")
        video_list.append({
            "tag": video.tag,
            "video_id": video_id,
            "name": video.init_name,
            "subtime": subtime,
            "URL": URL,
            "error_video": error_video,
            "AI_status": AI_status,
            "AI_feedback": AI_feedback,
            "teacher_status": teacher_status,
            "teacher_feedback": teacher_feedback,
            "type": type_str
        })
    return JsonResponse({"status": 200, "videos": video_list})


@csrf_exempt
def stu2imgs(request):
    student_id = request.session.get('username')
    stu = Student.objects.get(username=student_id)
    img_list = []
    imgs = Image.objects.filter(student_ID=stu, homework_ID=1).all()
    for img in imgs:
        img_id = img.ID
        subtime = img.post_time
        name = img.URL.rsplit("/")[-1]
        URL = settings.POST_IMG_PATH + name
        if img.AI_status == True:
            AI_status = 1
            AI_feedback = img.AI_feedback
            if img.error_img != None:
                error_img = img.error_img
            else:
                error_img = None
        else:
            AI_status = 0
            AI_feedback = None
            error_img = None
        tea_feedback = ImgFeedback.objects.filter(img_ID=img_id).all()
        if tea_feedback.count() != 0:
            teacher_status = 1
            teacher_feedback = tea_feedback.first().content
            type_str = tea_feedback.first().type
        else:
            teacher_status = 0
            teacher_feedback = None
            type_str = "无"
        img_list.append({
            "img_id": img_id,
            "tag": img.tag,
            "name": name,
            "subtime": subtime,
            "URL": URL,
            "error_img": error_img,
            "AI_status": AI_status,
            "AI_feedback": AI_feedback,
            "teacher_status": teacher_status,
            "teacher_feedback": teacher_feedback,
            "type": type_str
        })
    return JsonResponse({"status": 200, "imgs": img_list})


def get_video_profile(request):
    user_id = request.session.get('username')
    user = User.objects.get(username=user_id)
    video_ID = request.POST.get('video_id')
    video = Video.objects.get(ID=video_ID)
    if user.is_staff:
        teacher = Teacher.objects.get(username=user_id)
        teacher_read_video = TeacherRVideo.objects.get(teacher_ID=teacher, video_ID=video)
        teacher_read_video.read = "1"
        teacher_read_video.save()
    subtime = video.post_time
    name = video.URL.rsplit("/")[-1]
    URL = settings.POST_VIDEO_PATH + name
    if video.AI_status == True:
        AI_status = 1
        AI_feedback = video.AI_feedback
        if video.error_video != None:
            error_video = video.error_video
        else:
            error_video = None
    else:
        AI_status = 0
        AI_feedback = None
        error_video = None
    tea_feedback = VidFeedback.objects.filter(video_ID=video_ID).all()
    teacher_feedback_list = []
    type_str = "无"
    if tea_feedback.count() != 0:
        teacher_status = 1
        for feedback in tea_feedback:
            teacher_feedback_list.append(feedback.content)
        type_str = tea_feedback.first().type
    else:
        teacher_status = 0
        teacher_feedback_list = None
        type_str = "无"
    return JsonResponse({
        "video_id": video_ID,
        "name": name,
        "subtime": subtime,
        "URL": URL,
        "error_video": error_video,
        "AI_status": AI_status,
        "AI_feedback": AI_feedback,
        "teacher_status": teacher_status,
        "teacher_feedback": teacher_feedback_list,
        "type": type_str
    })


@csrf_exempt
def get_img_profile(request):
    user_id = request.session.get('username')
    img_id = request.POST.get('img_id')
    print(user_id)
    print(img_id)
    img = Image.objects.get(ID=img_id)
    subtime = img.post_time
    name = img.URL.rsplit("/")[-1]
    URL = settings.POST_IMG_PATH + name

    if get_role(user_id) == 1:
        teacher = Teacher.objects.get(username=user_id)
        teacher_read_image = TeacherRImage.objects.get(teacher_ID=teacher, image_ID=img)
        teacher_read_image.read = "1"
        teacher_read_image.save()

    type_str = "无"
    if img.AI_status == True:
        AI_status = 1
        AI_feedback = img.AI_feedback
        if img.error_img != None:
            error_img = settings.ERROR_IMG_PATH + img.error_img.rsplit("/")[-1]
        else:
            error_img = None
    else:
        AI_status = 0
        AI_feedback = None
        error_img = None
    error_img = URL
    tea_feedback = ImgFeedback.objects.filter(img_ID=img_id).all()
    teacher_feedback_list = []
    if tea_feedback.count() != 0:
        teacher_status = 1
        for feedback in tea_feedback:
            teacher_feedback_list.append(feedback.content)
        type_str = tea_feedback.first().type
    else:
        teacher_status = 0
        teacher_feedback_list = None
        type_str = "无"
    return JsonResponse({
        "img_id": img_id,
        "name": name,
        "subtime": subtime,
        "URL": URL,
        "error_img": error_img,
        "AI_status": AI_status,
        "AI_feedback": AI_feedback,
        "teacher_status": teacher_status,
        "teacher_feedback": teacher_feedback_list,
        "type": type_str
    })


# def parse_excel(attendance_sheet, student_ids, student_names, student_majors):
#     excel_file = pd.ExcelFile(attendance_sheet, engine='xlrd')
#     df = pd.read_excel(excel_file, 'Sheet1')
#     weekday_mapping = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "日": "7", "天": "7"}
#     row_0 = df.iloc[0].tolist()
#     row_1 = df.iloc[1].tolist()
#     row_2 = df.iloc[2].tolist()
#     course_number = row_0[0].split("：")[1].strip()  # 课程代号
#     course_name = row_0[4].split("：")[1].strip()  # 课程名称
#     teacher = row_1[4].split("：")[1].strip()  # 任课教师
#     time_str = row_2[0][:20]
#     pattern = re.compile(r'(\S+周)星期(\S+)第((?:\d+,)*\d+)节*')
#     matches = pattern.match(time_str)
#     week_range = matches.group(2)
#     weekday = weekday_mapping.get(matches.group(2))
#     start_time = matches.group(3).split(',')[0].strip()
#     end_time = matches.group(3).split(',')[-1].strip()
#
#     row_index = 5  # 从第五行开始
#     while row_index < len(df) and not pd.isna(df.iloc[row_index, 0]):
#         row_values = df.iloc[row_index].tolist()
#         student_ids.append(row_values[1])
#         student_names.append(row_values[2])
#         student_majors.append(row_values[5])
#         row_index += 1
#     return [course_number, course_name, teacher, start_time, end_time, weekday]


# def parse_excel(attendance_sheet, student_ids, student_names, student_majors):
#     print("start parse")
#     df = pd.read_excel(attendance_sheet)
#     ids = df.iloc[:, [1]].values[6:]
#     names = df.iloc[:, [2]].values[6:]

#     index = 0
#     while index < len(ids):
#         if not pd.isnull(ids[index][0]):
#             student_ids.append(ids[index][0])
#             student_names.append(names[index][0])
#         index += 1

#     course_number = df.iloc[2].values[1]
#     teacher = df.iloc[2].values[12][6:]
#     time_str = df.iloc[3].values[5]

#     # pattern = re.compile(r'(\S+周) 星期(\S+) 第((?:\d+,)*\d+)节*')
#     course_name = df.iloc[2].values[5]
#     start_time = time_str
#     return [course_number, course_name, teacher, start_time," end_time", "weekday"]

def parse_excel(attendance_sheet, student_ids, student_names, student_majors):
    print("start parse")
    df = pd.read_excel(attendance_sheet)
    ids = df.iloc[:, [3]].values[3:]
    names = df.iloc[:, [4]].values[3:]

    index = 0
    while index < len(ids):
        if not pd.isnull(ids[index][0]):
            student_ids.append(ids[index][0])
            student_names.append(names[index][0])
        index += 1

    course_number = "默认课程号"
    teacher = df.iloc[0].values[28]
    time_str = df.iloc[0].values[3]

    # pattern = re.compile(r'(\S+周) 星期(\S+) 第((?:\d+,)*\d+)节*')
    course_name = df.iloc[0].values[13]
    start_time = time_str
    return [course_number, course_name, teacher, start_time, " end_time", "weekday"]


# def create_class(request):
#     user_id = request.session.get('username')
#     try:
#         semester = "2024_spring"
#         if not Semester.objects.filter(semester_name=semester).exists():
#             Semester.objects.create(
#                 semester_name=semester
#             )
#         semobj = Semester.objects.get(semester_name=semester)
#         teacher = Teacher.objects.get(username=user_id)
#
#         attendance_sheet = request.FILES.get("attendance_sheet")
#         student_ids = []
#         student_names = []
#         student_majors = []
#         [none, course_name, none, start_time, end_time, weekday] = parse_excel(attendance_sheet, student_ids,
#                                                                                student_names, student_majors)
#         class_instance = Class.objects.create(
#             semester=semobj,
#             teacher_ID=teacher,
#             sport="排球",
#             name=course_name,
#             start_time=str(start_time),
#             end_time=str(end_time)
#         )
#
#         for student_id, student_name in zip(student_ids, student_names):
#             # 检查数据库中是否已存在该学号对应的 Student 对象
#             existing_student = Student.objects.filter(username=student_id).first()
#             if not existing_student:
#                 Student.objects.create_user(username=student_id, password='666666', first_name=student_name,
#                                             major='默认专业', pwd="666666")
#                 print(f"Student {student_id} created with name {student_name}.")
#             else:
#                 print(f"Student {student_id} already exists.")
#
#         students_to_add = Student.objects.filter(username__in=student_ids)
#         for student in students_to_add:
#             student_class_instance = Student_class(class_ID=class_instance, student_ID=student)
#             student_class_instance.save()
#
#         teacher_class_instance = Teacher_class(teacher_ID=teacher, class_ID=class_instance)
#         teacher_class_instance.save()
#
#         return JsonResponse({"status": 200})
#     except ObjectDoesNotExist as e:
#         return JsonResponse({"status": 400, "msg": e})


def create_class(request):
    user_id = request.session.get('username')
    school = request.POST.get('school')
    name = request.POST.get('name')
    start_time = request.POST.get('start_time')

    try:
        semester = "2024_spring"
        if not Semester.objects.filter(semester_name=semester).exists():
            Semester.objects.create(semester_name=semester)
            semobj = Semester.objects.get(semester_name=semester)
            teacher = Teacher.objects.get(username=user_id)

        while True:
            invite_code = generate_random_str()
            try:
                Class.objects.get(end_time=invite_code)
            except ObjectDoesNotExist:
                break

            class_instance = Class.objects.create(
                    semester=semobj,
                    teacher_ID=teacher,
                    sport=school,
                    name=name,
                    start_time=start_time,
                    end_time=invite_code
                )

        teacher_class_instance = Teacher_class(teacher_ID=teacher, class_ID=class_instance)
        teacher_class_instance.save()

        return JsonResponse({"status": 200, "invite_code": invite_code})

    except ObjectDoesNotExist as e:
        return JsonResponse({"status": 400, "msg": e})


def tea2classes(request):
    print(request.method)
    try:
        user_id = request.session.get('username')
        sem = request.POST.get('sem', "2024_spring")
        teacher = Teacher.objects.get(username=user_id)
        semester = Semester.objects.get(semester_name=sem)
        classes = Class.objects.filter(teacher_ID=teacher, semester=semester).all()
        class_list = []
        for item in classes:
            class_list.append({
                "class_id": item.ID,
                "semester": model_to_dict(semester),  # 将 Semester 对象转换为字典
                "sport": item.sport,
                "name": item.name,
                "start_time": item.start_time,
                "end_time": item.end_time
            })
        return JsonResponse({
            "status": 200,
            "classes": class_list
        })

    except Teacher.DoesNotExist:
        return JsonResponse({"status": 404, "error": "Teacher not found"})

    except Semester.DoesNotExist:
        return JsonResponse({"status": 404, "error": "Semester not found"})

    except Exception as e:
        return JsonResponse({"status": 500, "error": str(e)})


from django.db.models import Case, Value, When, ExpressionWrapper, Q, CharField


def classe_addin_list(classe, student_list):
    student_images = TeacherRImage.objects.filter(read="0").values_list("image_ID__student_ID").distinct()
    student_videos = TeacherRVideo.objects.filter(read="0").values_list("video_ID__student_ID").distinct()
    student_videos = student_videos.union(student_images)
    # print(student_ids)

    students = Student.objects.filter(
        student_class__class_ID=classe.ID,
    ).annotate(read_msg=Case(
        When(id__in=student_videos, then=Value("0")),
        default=Value("1"),
        output_field=CharField(max_length=128)
    ))
    for student in students:
        student_dict = {
            "student_id": student.last_name,
            "student_name": student.first_name,
            "read_msg": student.read_msg
        }
        student_list.append(student_dict)


def class2students(request):
    user_id = request.session.get('username')
    user = User.objects.get(username=user_id)
    if user.is_staff == 0:
        return JsonResponse({"status": 400})

    class_id = request.POST.get('class_id')
    place = "上课地点：北京航空航天大学"
    try:
        classe = Class.objects.get(ID=class_id)
        student_list = []
        place = classe.start_time
        classe_addin_list(classe, student_list)
    except Class.DoesNotExist:
        return JsonResponse({"status": 401})

    return JsonResponse({
        "status": 200,
        "place": place,
        "students": student_list
    })


def tea2students(request):
    user_id = request.session.get('username')
    try:
        class_ids = []
        for class_obj in Class.objects.all():
            if str(class_obj.teacher_ID) == str(user_id):
                class_ids.append(class_obj.ID)
        student_list = []
        for class_id in class_ids:
            try:
                classe = Class.objects.get(ID=class_id)
                classe_addin_list(classe, student_list)
            except Class.DoesNotExist:
                return JsonResponse({"status": 400})
    except Teacher_class.DoesNotExist:
        return JsonResponse({"status": 401})

    return JsonResponse({
        "status": 200,
        "students": student_list
    })


######################### 2023-10-3 23:33 by wbx
def tea2stu2videos(request):
    teacher_id = request.session.get('username')
    teacher = Teacher.objects.get(username=teacher_id)
    stu_id = request.POST.get('student_id')
    stu = Student.objects.get(username=stu_id)
    if stu is None:
        return JsonResponse({"status": 400})

    video_list = []
    videos = Video.objects.filter(student_ID=stu).all()
    for video in videos:
        video_ID = video.ID
        subtime = video.post_time
        name = video.URL.rsplit("/")[-1]
        img_name = (video.URL.rsplit("/")[-1]).rsplit(".")[0]
        URL = settings.POST_VIDEO_PATH + name
        if video.AI_status == True:
            AI_status = 1
            AI_feedback = video.AI_feedback
            if video.error_video != None:
                error_video = settings.ERROR_VIDEO_PATH + video.error_video.rsplit("/")[-1]
            else:
                error_video = None
        else:
            AI_status = 0
            AI_feedback = None
            error_video = None
        tea_feedback = VidFeedback.objects.filter(video_ID=video_ID).all()
        if tea_feedback.count() != 0:
            teacher_status = 1
            teacher_feedback = tea_feedback.first().content
        else:
            teacher_status = 0
            teacher_feedback = None
        print("Hey")
        print(teacher.last_name)
        print(video.ID)
        try:
            teacher_read_video = TeacherRVideo.objects.get(teacher_ID=teacher, video_ID=video)
            video_list.append({
                "video_id": video_ID,
                "name": video.init_name,
                "student_name": video.homework_ID.name,
                "subtime": subtime,
                "URL": URL,
                "error_video": error_video,
                "AI_status": AI_status,
                "AI_feedback": AI_feedback,
                "teacher_status": teacher_status,
                "teacher_feedback": teacher_feedback,
                "read": teacher_read_video.read,
                "tag": video.tag
            })
        except:
            continue
    return JsonResponse({"status": 200, "videos": video_list})


def tea2stu2imgs(request):
    teacher_id = request.session.get('username')
    teacher = Teacher.objects.get(username=teacher_id)
    stu_id = request.POST.get('student_id')
    stu = Student.objects.get(username=stu_id)
    if stu is None:
        return JsonResponse({"status": 400})
    else:
        img_list = []
        imgs = Image.objects.filter(student_ID=stu).all()
        print(imgs.count)
        for img in imgs:
            img_ID = img.ID
            subtime = img.post_time
            name = img.URL.rsplit("/")[-1]
            URL = settings.POST_IMG_PATH + name
            if img.AI_status == True:
                AI_status = 1
                AI_feedback = img.AI_feedback
                if img.error_img != None:
                    error_img = settings.ERROR_IMG_PATH + img.error_img.rsplit("/")[-1]
                else:
                    error_img = None
            else:
                AI_status = 0
                AI_feedback = None
                error_img = None
            tea_feedback = ImgFeedback.objects.filter(img_ID=img_ID).all()
            if tea_feedback.count() != 0:
                teacher_status = 1
                teacher_feedback = tea_feedback.first().content
            else:
                teacher_status = 0
                teacher_feedback = None
            print("Hey")
            print(teacher.last_name)
            print(img.ID)
            try:
                teacher_read_image = TeacherRImage.objects.get(teacher_ID=teacher, image_ID=img)
                img_list.append({
                    "img_id": img_ID,
                    "name": name,
                    "student_name": img.homework_ID.name,
                    "subtime": subtime,
                    "URL": URL,
                    "error_img": error_img,
                    "AI_status": AI_status,
                    "AI_feedback": AI_feedback,
                    "teacher_status": teacher_status,
                    "teacher_feedback": teacher_feedback,
                    "read": teacher_read_image.read,
                    "tag": img.tag
                })
            except TeacherRImage.DoesNotExist:
                continue
        return JsonResponse({"status": 200, "imgs": img_list})


def add_student(request):
    student_id = request.POST.get("student_id")
    class_id = request.POST.get("class_id")
    name = request.POST.get("name")

    classe = Class.objects.get(ID=class_id)

    try:
        stu = Student.objects.get(username=student_id)
    except ObjectDoesNotExist:
        stu = Student.objects.create_user(
            pwd="666666",
            username=student_id,
            password="666666",
            first_name=name,
            is_staff=0  # 0->学生 1->老师
        )

    Student_class.objects.create(student_ID=stu, class_ID=classe)

    return JsonResponse({"status": 200})


def teacher_change_class_name(request):
    teacher_id = request.session.get("username")
    class_id = request.POST.get("class_id")
    class_name = request.POST.get("new_name")
    classe = Class.objects.get(ID=class_id)
    if (str(classe.teacher_ID) != str(teacher_id)):
        return JsonResponse({"status": 400})
    classe.name = class_name
    classe.save()
    return JsonResponse({"status": 200})


def teacher_add_videofeedback(request):
    teacher_id = request.session.get('username')
    video_id = request.POST.get('video_id')
    feedback = request.POST.get('feedback')
    type = request.POST.get('type')
    map = ["无评价", "ai判断正确", "ai错判", "ai误判"]
    print(feedback)
    print("请输入发聩意见")
    print(f"{feedback != '请输入发聩意见'}")
    video = Video.objects.get(ID=video_id)
    if video is None:
        return JsonResponse({"status": 401, "error_msg": "Do not have " + video_id + " video"})
    teacher = Teacher.objects.get(username=teacher_id)
    if teacher is None:
        return JsonResponse({"status": 402, "error_msg": "Do not have " + teacher_id + " teacher"})

    try:
        vid = VidFeedback.objects.get(video_ID=video_id)
        if feedback != '请输入发聩意见':
            vid.content = feedback
        if int(type) != 0:
            vid.type = map[int(type)]
        vid.save()
    except ObjectDoesNotExist:
        VidFeedback.objects.create(
            video_ID=video,
            teacher_ID=teacher,
            content=feedback,
            type=map[int(type)]
        )
    return JsonResponse({"type": map[int(type)]})


def teacher_add_imgfeedback(request):
    teacher_id = request.session.get('username')
    img_id = request.POST.get('img_id')
    feedback = request.POST.get('feedback')
    type = request.POST.get('type')
    map = ["无评价", "ai判断正确", "ai错判", "ai误判"]

    img = Image.objects.get(ID=img_id)
    if img is None:
        return JsonResponse({"status": 401, "error_msg": "Do not have " + img_id + " video"})
    teacher = Teacher.objects.get(username=teacher_id)
    if teacher is None:
        return JsonResponse({"status": 402, "error_msg": "Do not have " + teacher_id + " teacher"})

    try:
        image = ImgFeedback.objects.get(img_ID=img_id)
        if feedback != "请输入发聩意见":
            image.content = feedback
        if int(type) != 0:
            image.type = map[int(type)]
        image.save()
    except ObjectDoesNotExist:
        ImgFeedback.objects.create(
            img_ID=img,
            teacher_ID=teacher,
            content=feedback,
            type=map[int(type)]
        )
    return JsonResponse({"type": map[int(type)]})


def delete_img(request):
    img_id = request.POST.get('img_id')
    student_id = request.session.get('username')
    stu = Student.objects.get(username=student_id)

    try:
        image = Image.objects.get(ID=img_id, student_ID=stu)
        image.delete()
        os.remove(image.URL)
        print(f"文件 {image.URL} 已成功删除")
        return JsonResponse({"status": 200, "msg": "删除图片" + img_id})
    except ObjectDoesNotExist:
        return JsonResponse({"status": 400, "msg": "图片不存在或不属于该学生"})


def delete_video(request):
    video_id = request.POST.get('video_id')
    user_id = request.session.get('username')
    stu = Student.objects.get(username=user_id)
    try:
        video = Video.objects.get(ID=video_id, student_ID=stu)
        video.delete()
        os.remove(video.URL)
        print(f"文件 {video.URL} 已成功删除")
        return JsonResponse({"status": 200, "msg": "删除视频" + video_id})
    except ObjectDoesNotExist:
        return JsonResponse({"status": 400, "msg": "视频不存在或不属于该用户"})


def teapub_notice(request):
    class_id = request.POST.get('class_id')
    text = request.POST.get('text')
    teacher_id = request.session.get('username')
    teacher = Teacher.objects.get(username=teacher_id)
    fn = (datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    try:
        classe = Class.objects.get(ID=class_id, teacher_ID=teacher)
        notice = Notice.objects.create(
            class_ID=classe,
            text=text,
            time=fn
        )
        student_class = Student_class.objects.filter(class_ID=classe)
        for relation in student_class:
            StudentRNotice.objects.create(
                student_ID=Student.objects.get(username=relation.student_ID),
                notice_ID=notice,
                read="0"
            )
        return JsonResponse({"status": 200})
    except Class.DoesNotExist:
        return JsonResponse({"status": 400})


def teapub_homework(request):
    teacher_id = request.session.get('username')
    teacher = Teacher.objects.get(username=teacher_id)
    class_id = request.POST.get('class_id')
    name = request.POST.get('name')
    explain = request.POST.get('explain')
    size_limit = request.POST.get('size', "20")
    limits = request.POST.get('type')

    print(size_limit)

    if size_limit and size_limit.isdigit():
        size_limit = int(size_limit)
    else:
        size_limit = 20

    dir = "None"
    hwFile = request.FILES.get('file')
    if hwFile:
        fn = time.strftime('%Y_%m_%d_%H_%M_%S')
        hw_name = fn + "_" + hwFile.name
        dir = settings.PUB_HW_DIR + str(hw_name)
        destination = open(dir, 'wb+')
        for chunk in hwFile.chunks():
            destination.write(chunk)
        destination.close()

    try:
        classe = Class.objects.get(ID=class_id, teacher_ID=teacher)
        current_date = datetime.now()
        if len(name) == 0:
            name = f"{current_date.strftime('%m月%d日')}作业"  # 根据日期生成作业名称
        if len(explain) == 0:
            explain = f"老师暂时没有添加作业说明~"
        Homework.objects.create(
            class_ID=classe,
            name=name,
            text=explain,
            size_limit=size_limit,
            type_limit=limits,
            file_dir=dir
        )
        return JsonResponse({"status": 200})
    except Class.DoesNotExist:
        return JsonResponse({"status": 400})


def tea2hw2info(request):
    class_id = request.POST.get('class_id')
    homework = Homework.objects.filter(class_ID=class_id)
    homework_list = []
    for work in homework:
        homework_id = work.ID
        homework_name = work.name
        homework_text = work.text
        homework_list.append({
            "homework_id": homework_id,
            "name": homework_name,
            "text": homework_text,
        })
    return JsonResponse({"status": 200, "homework_list": homework_list})


def tea2hw2profile(request):
    homework_id = request.POST.get('homework_id')
    videos = Video.objects.filter(homework_ID=homework_id)
    images = Image.objects.filter(homework_ID=homework_id)
    homework = Homework.objects.get(ID=homework_id)
    files = HomeworkFile.objects.filter(homework=homework).all()
    video_list = []
    image_list = []
    file_list = []
    for video in videos:
        student = Student.objects.get(username=video.student_ID)
        student_name = student.first_name
        teacher_feedback = VidFeedback.objects.filter(video_ID=video.ID).all()
        if teacher_feedback.count() != 0:
            teacher_status = 1
            tea_feedback = teacher_feedback.first().content
        else:
            teacher_status = 0
            tea_feedback = None
        video_list.append({
            "video_id": video.ID,
            "student_name": student_name,
            "name": None,
            "subtime": video.post_time,
            "URL": video.URL,
            "error_video": video.error_video,
            "AI_status": video.AI_status,  # (1表示已评判)
            "AI_feedback": video.AI_feedback,
            "teacher_status": teacher_status,  # (1表示已评判)
            "teacher_feedback": tea_feedback,
            "tag": video.tag
        })
    for image in images:
        student = Student.objects.get(username=image.student_ID)
        student_name = student.first_name
        teacher_feedback = ImgFeedback.objects.filter(img_ID=image.ID).all()
        if teacher_feedback.count() != 0:
            teacher_status = 1
            tea_feedback = teacher_feedback.first().content
        else:
            teacher_status = 0
            tea_feedback = None
        image_list.append({
            "img_id": image.ID,
            "student_name": student_name,
            "name": None,
            "subtime": image.post_time,
            "URL": image.URL,
            "error_img": image.error_img,
            "AI_status": image.AI_status,  # (1表示已评判)
            "AI_feedback": image.AI_feedback,
            "teacher_status": teacher_status,  # (1表示已评判)
            "teacher_feedback": tea_feedback,
            "tag": image.tag
        })
    for file in files:
        file_list.append({
            "file_id": file.ID,
            "student_name": file.init_name,
            "file_name": file.student.first_name + " " + homework.name,
            "URL": get_post_url(file.URL, settings.SUB_HW_PATH),
            "file_type": file.type
        })
    return JsonResponse({"status": 200, "imgs": image_list, "videos": video_list, "files": file_list})


def stu2hw2info(request):
    student_id = request.session.get('username')
    student = User.objects.get(username=student_id)
    class_objs = Student_class.objects.filter(student_ID=student)
    homework_list = []

    for class_obj in class_objs:
        homework_all = Homework.objects.filter(class_ID=class_obj.class_ID)
        for homework in homework_all:
            homework_list.append({
                "homework_id": homework.ID,
                "name": homework.name,
                "text": homework.text
            })

    return JsonResponse({"status": 200, "homework_list": homework_list})


def stu2hw2profile(request):
    homework_id = request.POST.get('homework_id')
    student_id = request.session.get('username')
    student = Student.objects.get(username=student_id)
    print(student.last_name)
    print(f"{homework_id}homework_id")
    video_list = []
    image_list = []
    file_list = []
    videos = Video.objects.filter(student_ID=student, homework_ID=homework_id).all()
    images = Image.objects.filter(student_ID=student, homework_ID=homework_id).all()
    files = HomeworkFile.objects.filter(student=student, homework=homework_id).all()
    for video in videos:
        video_feedback = VidFeedback.objects.filter(video_ID=video.ID).all()
        if video_feedback.count() != 0:
            teacher_status = 1
            teacher_feedback = video_feedback.first().content
        else:
            teacher_status = 0
            teacher_feedback = None
        name = video.URL.rsplit("/")[-1]
        URL = settings.POST_VIDEO_PATH + name
        video_list.append({
            "video_id": video.ID,
            "name": None,
            "subtime": video.post_time,
            "URL": URL,
            "error_video": video.error_video,
            "AI_status": video.AI_status,
            "AI_feedback": video.AI_feedback,
            "teacher_status": teacher_status,
            "teacher_feedback": teacher_feedback
        })
    for image in images:
        image_feedback = ImgFeedback.objects.filter(img_ID=image.ID).all()
        if image_feedback.count() != 0:
            tea_status = 1
            tea_feedback = image_feedback.first().content
        else:
            tea_status = 0
            tea_feedback = None
        name = image.URL.rsplit("/")[-1]
        URL = settings.POST_VIDEO_PATH + name
        image_list.append({
            "img_id": image.ID,
            "name": None,
            "subtime": image.post_time,
            "URL": URL,
            "error_img": image.error_img,
            "AI_status": image.AI_status,
            "AI_feedback": image.AI_feedback,
            "teacher_status": tea_status,
            "teacher_feedback": tea_feedback
        })
    for file in files:
        file_list.append({
            "file_id": file.ID,
            "student_name": file.student.first_name,
            "file_name": file.init_name,
            "URL": get_post_url(file.URL, settings.SUB_HW_PATH),
            "file_type": file.type
        })
    homework = Homework.objects.get(ID=homework_id)
    hw_url = get_post_url(homework.file_dir, settings.PUB_HW_PATH)
    hw_url_type = hw_url.rsplit('.')[-1]
    print({"status": 200, "imgs": image_list, "videos": video_list, "files": file_list,  # 这三个数组是学生已经提交的，用来回显
           "file": hw_url, "type": hw_url_type})
    return JsonResponse(
        {"status": 200, "imgs": image_list, "videos": video_list, "files": file_list,  # 这三个数组是学生已经提交的，用来回显
         "file": hw_url, "type": hw_url_type})  # 这个file是老师布置作业的时候发布的，可能是示范视频、格式模板等等


def stu2notice(request):
    notice_list = []
    open_id = request.headers.get('')
    student_id = request.session.get("username")
    if get_role(student_id) == 1:
        class_id = request.POST.get('class_id')
        class_notice = Notice.objects.filter(class_ID=class_id)
        for notice in class_notice:
            notice_list.append({
                "notice_id": notice.ID,
                "text": notice.text,
                "time": notice.time,
                "read": "1"
            })
    else:
        student = Student.objects.get(username=student_id)
        scs = Student_class.objects.filter(student_ID=student)
        for s_c in scs:
            class_notice = Notice.objects.filter(class_ID=s_c.class_ID)
            for notice in class_notice:
                try:
                    student_notice = StudentRNotice.objects.get(student_ID=student, notice_ID=notice)
                    notice_list.append({
                        "notice_id": notice.ID,
                        "text": notice.text,
                        "time": notice.time,
                        "read": student_notice.read
                    })
                except ObjectDoesNotExist:
                    continue

    return JsonResponse({"status": 200, "notice": notice_list})


def student_read_notice(request):
    notice_id = request.POST.get("notice_id")
    notice = Notice.objects.get(ID=notice_id)
    student = Student.objects.get(username=request.session.get("username"))
    student_notice = StudentRNotice.objects.get(student_ID=student, notice_ID=notice)
    student_notice.read = "1"
    student_notice.save()
    return JsonResponse({"status": 200})


def database_init(request):
    teacher = Teacher.objects.create(
        username="18111105",
        password="666666",
        first_name="SuperManager",
        is_staff=1
    )
    semester = "2023_fall"
    if not Semester.objects.filter(semester_name=semester).exists():
        Semester.objects.create(
            semester_name=semester
        )
    semobj = Semester.objects.get(semester_name=semester)
    init_class = Class.objects.create(
        semester=semobj,
        teacher_ID=teacher,
        sport="排球自主练习",
        name="排球自主练习",
        start_time="1_1",
        end_time="7_13"
    )
    Homework.objects.create(
        class_ID=init_class,
        name="自主练习",
        text="这里是提供给同学们自主练习的，并可以查看AI评价与老师评价",
        size_limit=64,
        type_limit="mp4_jpg_png_jpeg_mov_avi",
        file_dir=dir
    )
    if Homework.objects.count() == 1:
        return JsonResponse({"status": 200})
    else:
        return JsonResponse({"status": 400})


def del_err(request):
    Image.objects.filter(AI_status=False).delete()
    Video.objects.filter(AI_status=False).delete()
    return JsonResponse({"msg": "删除AI未检测图片及视频"})


def redo(request):
    imgs = Image.objects.filter(AI_status=False).all()
    for img in imgs:
        # openpose.delay(temp.img_ID, img_URL, 1)
        openpose.delay(img.ID, img.URL, 1)
    vids = Video.objects.filter(AI_status=False).all()
    for vid in vids:
        openpose.delay(vid.ID, vid.URL, 0)
    return JsonResponse({"msg": "重新检测AI未检测的图片及视频"})


def student_get_material(request):
    file_list = []
    student_id = request.session.get("username")
    if get_role(student_id) == 1:
        class_id = request.POST.get('class_id')
        print("class_id")
        print(class_id)
        files = Material.objects.filter(class_id=class_id)
        for file in files:
            file_list.append({
                'url': file.url,
                'type': file.type,
                'explain': file.explain,
                'init_name': file.init_name,
            })
    else:
        student = Student.objects.get(username=student_id)
        stu_class_objs = Student_class.objects.filter(student_ID=student)
        for classe in stu_class_objs:
            files = Material.objects.filter(class_id=classe.class_ID)
            for file in files:
                file_list.append({
                    'url': file.url,
                    'type': file.type,
                    'explain': file.explain,
                    'init_name': file.init_name,
                })
    print("hey")
    print(file_list)
    return JsonResponse({'status': 200, 'file_list': file_list})


def teacher_add_material(request):
    teacher_id = request.session.get('username')
    class_id = request.POST.get('class_id')
    explain = request.POST.get('explain')
    file = request.FILES.get("file")
    suffix = file.name.rsplit(".")[-1]
    teacher = Teacher.objects.get(username=teacher_id)
    file_name = explain + "." + suffix

    dir = settings.TEACH_MATERIAL_DIR + str(file_name)
    destination = open(dir, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    url = settings.TEACH_MATERIAL_PATH + str(file_name)
    classe = Class.objects.get(ID=class_id)
    Material.objects.create(
        url=url,
        explain=(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
        type=suffix,
        class_id=classe,
        init_name=file_name,
    )

    return JsonResponse({"status": 200})


def student_getSignList(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    username = request.session.get('username')
    student = Student.objects.get(username=username)
    studentClass = Student_class.objects.filter(student_ID=student)
    for scs in studentClass:
        signs = Sign.objects.filter(classe=scs.class_ID).all()
        result = []
        for sign in signs:
            try:
                relation = StudentSign.objects.get(sign=sign, student=student)
                result.append({
                    "sign_id": sign.id,
                    "name": sign.name,
                    "state": relation.state,
                    "message": relation.message,
                    "timeout": sign.threshold_minutes
                })
            except ObjectDoesNotExist:
                continue
    return JsonResponse({"status": 200, "signs": result})


def student_signin(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})
    student_id = request.session.get('username')
    student = Student.objects.get(username=student_id)
    sign_id = request.POST.get('sign_id')
    sign = Sign.objects.get(id=sign_id)
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    signTime = request.POST.get('signTime')
    distance = haversine(latitude, longitude, sign.latitude, sign.longitude)
    print(student_id)
    print(student.first_name)
    print("进行签到 ！")
    print(f"当前时间 {datetime.now() + timedelta(hours=8)}")
    try:
        print(f"截止时间 {datetime.strptime(sign.threshold_minutes, '%Y-%m-%d %H:%M:%S')}")
    except:
        print("解析时间格式错误！")
    # ok_time = is_time_difference_within_threshold(signTime, sign.time, threshold_minutes=sign.threshold_minutes)  # 目前默认设为5分钟
    ok_time = datetime.now() + timedelta(hours=8) < datetime.strptime(sign.threshold_minutes, "%Y-%m-%d %H:%M:%S")
    print(f"{ok_time} 时间符合要求")
    if distance < settings.VALID_DISTANCE and ok_time:
        studentSign = StudentSign.objects.get(student=student, sign=sign)
        if studentSign.state:
            print(f"distance: {distance}, limit:{settings.VALID_DISTANCE} 重复")
            return JsonResponse({"status": 403, "distance": distance, "limit": settings.VALID_DISTANCE})  # 重复签到
        studentSign.state = True
        studentSign.message = "已签到"
        studentSign.save()
        print(f"distance: {distance}, limit:{settings.VALID_DISTANCE} success ")
        return JsonResponse({"status": 200, "distance": distance, "limit": settings.VALID_DISTANCE})
    elif not ok_time:
        print(f"distance: {distance}, limit:{settings.VALID_DISTANCE} time exceed")
        return JsonResponse({"status": 402, "distance": distance, "limit": settings.VALID_DISTANCE})  # 时间超时
    else:
        print(f"distance: {distance}, limit:{settings.VALID_DISTANCE} position exceed")
        return JsonResponse({"status": 401, "distance": distance, "limit": settings.VALID_DISTANCE})  # 位置有误


def teapub_sign(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    class_id = request.POST.get('class_id')
    time_now = (datetime.now() + timedelta(hours=8)).strftime('%m-%d %H:%M:%S')
    name = request.POST.get('name', f'未命名签到-{time_now}')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    interval = request.POST.get('threshold_minutes')
    print(f"老师发布签到 限制时间为 {interval}分钟")
    try:
        threshold_minutes = (datetime.now() + timedelta(hours=8) + timedelta(minutes=int(interval))).strftime(
            "%Y-%m-%d %H:%M:%S")  # 默认值是5
    except Exception:
        threshold_minutes = (datetime.now() + timedelta(hours=8) + timedelta(minutes=5)).strftime(
            "%Y-%m-%d %H:%M:%S")

    current_time = datetime.now() + timedelta(hours=8)
    formatted_time = current_time.strftime('%Y-%m-%d-%H:%M:%S')
    sign = Sign.objects.create(classe_id=class_id, name=name, time=formatted_time, latitude=latitude,
                               longitude=longitude, threshold_minutes=threshold_minutes)
    student_classes = Student_class.objects.filter(class_ID=class_id).all()
    for student_class in student_classes:
        student = student_class.student_ID
        StudentSign.objects.create(student=student, sign=sign, state=False, message="未签到")
    sign_id = sign.id
    return JsonResponse({"id": sign_id, "end_time": threshold_minutes})


def tea_modify_signTime(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    sign_id = request.POST.get('sign_id')
    sign = Sign.objects.get(id=sign_id)
    interval = request.POST.get('threshold_minutes')

    first_data = datetime.strptime(sign.threshold_minutes, "%Y-%m-%d %H:%M:%S")
    try:
        end_time = first_data + timedelta(minutes=int(interval))
    except Exception:
        end_time = first_data + timedelta(minutes=5)
    sign.threshold_minutes = end_time.strftime('%Y-%m-%d %H:%M:%S')
    sign.save()

    return JsonResponse({"status": 200, "end_time": sign.threshold_minutes})


def teamodify_sign(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    sign_id = request.POST.get('sign_id')
    sign = Sign.objects.get(id=sign_id)
    student_id = request.POST.get("student_id")
    student = Student.objects.get(username=student_id)
    state = request.POST.get('state')
    print(f"前端传过来的state是 {state}")
    print(len(state))
    studentSign = StudentSign.objects.get(student=student, sign=sign)
    if state != "":
        print("修改为 已签到")
        studentSign.state = True
        studentSign.message = "已签到"
        studentSign.save()
    else:
        print("修改为 未签到")
        studentSign.state = False
        studentSign.message = "未签到"
        studentSign.save()
    print(f"修改完毕！")
    return JsonResponse({"status": 200})


def teaget_signprofile(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    sign_id = request.POST.get('sign_id')
    sign = Sign.objects.get(id=sign_id)
    classe_id = request.POST.get("class_id")
    classe = Class.objects.get(ID=classe_id)

    studentClasses = Student_class.objects.filter(class_ID=classe).all()

    result = []
    for studentClass in studentClasses:
        student = studentClass.student_ID
        try:
            studentSign = StudentSign.objects.get(student=student, sign=sign)
            result.append({
                "student_username": student.last_name,
                "student_name": student.first_name,
                "state": studentSign.state,
                "message": studentSign.message
            })
        except ObjectDoesNotExist:
            continue

    return JsonResponse({"status": 200, "result": result})


def teaget_stufiles(request):
    student_id = request.POST.get('student_id')
    stu = Student.objects.get(username=student_id)

    hwfiles = HomeworkFile.objects.filter(student=stu).all()
    result = []
    for hwfile in hwfiles:
        URL = settings.SUB_HW_PATH + time.strftime('%Y_%m_%d_%H_%M_%S') + "_" + hwfile.init_name
        result.append({
            "URL": URL,
            "file_name": stu.first_name + " " + hwfile.homework.name,
            "student_name": hwfile.init_name,
            "file_type": hwfile.type
        })

    return JsonResponse({"status": 200, "result": result})


def teaget_sign(request):
    if request.method != 'POST':
        return JsonResponse({"status": 500})

    class_id = request.POST.get('class_id')
    signs = Sign.objects.filter(classe_id=class_id).all()

    result = []
    for sign in signs:
        result.append({
            "sign_id": sign.id,
            "name": sign.name,
            "endTime": sign.threshold_minutes
        })

    return JsonResponse({"status": 200, "result": result})


def stu_sub_hw(request):
    student_id = request.session.get('username')
    homework_id = request.POST.get('homework_id')
    file = request.FILES.get('file')

    suffix = file.name.split('.')[-1]
    file_name = f"{student_id}_{(datetime.now() + timedelta(hours=8)).strftime('%Y_%m_%d_%H_%M_%S')}.{suffix}"
    # 存储图片在服务器本地
    dir = settings.SUB_HW_DIR + str(file_name)
    init_name = f"{student_id}-{(datetime.now() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')}.{suffix}"
    destination = open(dir, 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    student = Student.objects.get(username=student_id)
    homework = Homework.objects.get(ID=homework_id)

    try:
        hw = HomeworkFile.objects.get(student=student, homework=homework)
        # 如果存在对应的记录，更新它的属性
        hw.init_name = init_name
        hw.type = suffix
        hw.URL = dir
        hw.save()
    except HomeworkFile.DoesNotExist:
        # 如果记录不存在，创建一个新的记录
        HomeworkFile.objects.create(
            student=student,
            homework=homework,
            init_name=init_name,
            type=suffix,
            URL=dir
        )

    return JsonResponse({"status": 200})


def RemoteDispatch(request):
    if request.POST.get("pwd") != sha256:
        return JsonResponse({"status": 400})
    image = Image.objects.filter(AI_status=False).order_by('post_time').first()
    if image:
        print(f"视频上传时间 {image.post_time}")
        image_url = image.URL
        with open(image_url, 'rb') as video_file:
            video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        response_data = {
            "status": 200,
            "media_base64": video_base64,
            "tag": image.tag,
            "init_name": image_url.rsplit('/')[-1],
            "media_id": image.ID,
            "type": 1
        }
        return JsonResponse(response_data)
    else:
        print(f"当前无图片待处理")
    video = Video.objects.filter(AI_status=False).order_by('post_time').first()
    if video:
        print(f"视频上传时间 {video.post_time}")
        video_url = video.URL
        with open(video_url, 'rb') as video_file:
            video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        response_data = {
            "status": 200,
            "media_base64": video_base64,
            "tag": video.tag,
            "init_name": video_url.rsplit('/')[-1],
            "media_id": video.ID,
            "type": 0
        }
        return JsonResponse(response_data)
    return JsonResponse({"status": 204, "message": "暂无未处理的 视频和图片"})


def TaskFinished(request):
    if request.POST.get("pwd") != sha256:
        return JsonResponse({"status": 400})
    same_url = request.POST.get('same_url')
    media_base64 = request.POST.get('media_base64')
    media_name = request.POST.get('media_name')
    message = request.POST.get('message')
    id = request.POST.get('media_id')
    type = request.POST.get('type')

    if type == "0":
        video = Video.objects.get(ID=id)
        file_url = os.path.join(settings.ERROR_VIDEO_DIR, media_name)
        init_url = os.path.join(settings.POST_VIDEO_PATH, media_name)
        error_url = os.path.join(settings.ERROR_VIDEO_PATH, media_name)
        if same_url == "0":
            media_binary = base64.b64decode(media_base64)
            with open(file_url, 'wb') as f:
                f.write(media_binary)
            video.error_video = error_url
            print(f"视频传送成功 存入本地{file_url}")
            print(f"AI判定为 {message}")
        else:
            video.error_video = init_url
            print(f"无需传输视频")
            print(f"AI判定为 {message}")
        video.AI_feedback = message
        video.AI_status = True
        video.save()
    elif type == "1":
        image = Image.objects.get(ID=id)
        file_url = os.path.join(settings.ERROR_IMG_DIR, media_name)
        init_url = os.path.join(settings.POST_IMG_PATH, media_name)
        error_url = os.path.join(settings.ERROR_IMG_PATH, media_name)
        if same_url == "0":
            media_binary = base64.b64decode(media_base64)
            with open(file_url, 'wb') as f:
                f.write(media_binary)
            image.error_video = error_url
            print(f"图片传送成功 存入本地{file_url}")
            print(f"AI判定为 {message}")
        else:
            image.error_video = init_url
            print(f"无需传输图片")
            print(f"AI判定为 {message}")
        image = Image.objects.get(ID=id)
        image.error_img = error_url
        image.AI_feedback = message
        image.AI_status = True
        image.save()
    else:
        return JsonResponse({"status": 400})

    return JsonResponse({"status": 200})


def tea_reset_pwd(request):
    allow_tea = []
    teachers = Teacher.objects.all()
    for teacher in teachers:
        allow_tea.append(teacher.last_name)
    print(allow_tea)
    teacher_id = request.session.get('username')
    student_id = request.POST.get('id')
    if teacher_id in allow_tea:
        student = Student.objects.get(username=student_id)
        student.pwd = "666666"
        student.save()
    else:
        return JsonResponse({"status": 400})
    return JsonResponse({"status": 200})

def stuget_class_profile(request):
    invite_code = request.POST.get('invite_code')
    try:
        classe = Class.objects.get(end_time=invite_code)
        teacher_name = Teacher.objects.get(id=classe.teacher_ID.id).first_name

        return JsonResponse({
            "status": 200,
            "class_name": classe.name,
            "teacher_name": teacher_name,
            "school_id": classe.sport,
            "start_time": classe.start_time
        })
    except ObjectDoesNotExist:
        return JsonResponse({"status": 400, "msg": "没有班级"})


def stu_attend_class(request):
    username = request.session.get('username')
    invite_code = request.POST.get('invite_code')

    try:
        classe = Class.objects.get(end_time=invite_code)
        stu = Student.objects.get(username=username)

        try:
            Student_class.objects.get(student_ID=stu, class_ID=classe)
            return JsonResponse({"status": 400, "msg":"重复加入班级"})
        except ObjectDoesNotExist:
            student_class_instance = Student_class(class_ID=classe, student_ID=stu)
            student_class_instance.save()
            return JsonResponse({"status": 200})

    except ObjectDoesNotExist:
        return JsonResponse({"status": 400, "msg": "没有班级"})




    #ajsdkljalksj