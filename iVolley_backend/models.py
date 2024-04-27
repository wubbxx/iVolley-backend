from django.db import models
from django.contrib.auth.models import User


class Student(User):
    major = models.CharField(max_length=128, db_column='student_major')
    pwd = models.CharField(max_length=128, db_column="real_pwd")
    class Meta:
        db_table = 'student'

    def __str__(self):
        return self.username


class Teacher(User):
    major = models.CharField(max_length=128, db_column='teacher_major')
    pwd = models.CharField(max_length=128, db_column="real_pwd")
    def __str__(self):
        return self.username


class Homework(models.Model):
    ID = models.AutoField(primary_key=True, db_column='homework_id')
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID')
    name = models.CharField(max_length=128, db_column='homework_name')
    text = models.CharField(max_length=255, db_column='homework_text')
    end_time = models.CharField(max_length=255, db_column='end_time')
    file_dir = models.CharField(max_length=255, db_column='file_dir')
    type_limit = models.CharField(max_length=255, db_column='type_limit')
    size_limit = models.IntegerField(db_column='size_limit')

    class Meta:
        db_table = 'Homework'


class Notice(models.Model):
    ID = models.AutoField(primary_key=True, db_column='notice_ID')
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID')
    text = models.CharField(max_length=255, db_column='text')
    time = models.CharField(max_length=255, db_column='time')

    class Meta:
        db_table = 'Notice'


class StudentRNotice(models.Model):
    ID = models.AutoField(primary_key=True, db_column='stu_read_notice_id')
    student_ID = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')
    notice_ID = models.ForeignKey('Notice', on_delete=models.CASCADE, db_column='notice_ID')
    read = models.CharField(max_length=15, db_column='read')

    class Meta:
        db_table = 'Student_R_Notice'


class TeacherRVideo(models.Model):
    ID = models.AutoField(primary_key=True, db_column='tea_read_video_id')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    video_ID = models.ForeignKey('Video', on_delete=models.CASCADE, db_column='video_ID')
    read = models.CharField(max_length=15, db_column='read')

    class Meta:
        db_table = 'Teacher_R_Video'


class TeacherRImage(models.Model):
    ID = models.AutoField(primary_key=True, db_column='tea_read_image_id')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    image_ID = models.ForeignKey('Image', on_delete=models.CASCADE, db_column='image_ID')
    read = models.CharField(max_length=15, db_column='read')

    class Meta:
        db_table = 'Teacher_R_Image'


class Class(models.Model):
    ID = models.AutoField(primary_key=True, db_column='class_ID')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    semester = models.ForeignKey('Semester', on_delete=models.CASCADE, db_column='semester')
    sport = models.CharField(max_length=128, db_column='sport', default='未归类')
    name = models.CharField(max_length=128, db_column='class_name')
    start_time = models.CharField(max_length=128, db_column='start_time')
    end_time = models.CharField(max_length=128, db_column='end_time')

    class Meta:
        db_table = 'class'


class Task(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    title = models.CharField(max_length=255, db_column='title')
    content = models.TextField(db_column='content')
    release_time = models.DateTimeField(auto_now_add=True, db_column='release_time')
    deadline = models.DateTimeField(db_column='deadline')
    type = models.CharField(max_length=255, db_column='type')

    class Meta:
        db_table = 'task'



class Video(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    homework_ID = models.ForeignKey('Homework', on_delete=models.CASCADE, db_column='homework_ID', null=True)
    task_ID = models.ForeignKey('Task', on_delete=models.CASCADE, db_column='task_ID', null=True)
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID', null=True)
    student_ID = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')
    post_time = models.DateTimeField(auto_now_add=True, db_column='post_time')
    URL = models.TextField(max_length=1024, db_column='URL')
    AI_status = models.BooleanField(db_column='AI_status', default=False)
    AI_feedback = models.TextField(db_column='AI_feedback', null=True)
    error_video = models.TextField(max_length=1024, db_column='error_video', null=True)
    init_name = models.TextField(max_length=1024, db_column='init_name')
    tag = models.IntegerField(db_column='tag')

    class Meta:
        db_table = 'video'


class Image(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    homework_ID = models.ForeignKey('Homework', on_delete=models.CASCADE, db_column='homework_ID', null=True)
    task_ID = models.ForeignKey('Task', on_delete=models.CASCADE, db_column='task_ID', null=True)
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID', null=True)
    student_ID = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')
    post_time = models.DateTimeField(auto_now_add=True, db_column='post_time')
    URL = models.TextField(max_length=1024, db_column='URL')
    AI_status = models.BooleanField(db_column='AI_status', default=False)
    AI_feedback = models.TextField(db_column='AI_feedback', null=True)
    error_img = models.TextField(max_length=1024, db_column='error_img', null=True)
    tag = models.CharField(max_length=255, db_column='tag')

    class Meta:
        db_table = 'image'


class VidFeedback(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    video_ID = models.ForeignKey('Video', on_delete=models.CASCADE, db_column='video_ID')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    type = models.CharField(max_length=255, db_column='type')
    content = models.TextField(db_column='feedback_content')

    class Meta:
        db_table = 'vid_feedback'


class ImgFeedback(models.Model):
    ID = models.AutoField(primary_key=True, db_column='ID')
    img_ID = models.ForeignKey('Image', on_delete=models.CASCADE, db_column='img_ID')
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    type = models.CharField(max_length=255, db_column='type')
    content = models.TextField(db_column='content')


    class Meta:
        db_table = 'img_feedback'


class Semester(models.Model):
    semester_name = models.CharField(max_length=255, primary_key=True, db_column='semester_name')

    class Meta:
        db_table = 'semester'


class Student_class(models.Model):
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID')
    student_ID = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')

    class Meta:
        unique_together = ('class_ID', 'student_ID')
        db_table = 'student_class'


class Teacher_class(models.Model):
    teacher_ID = models.ForeignKey('Teacher', on_delete=models.CASCADE, db_column='teacher_ID')
    class_ID = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID')

    class Meta:
        unique_together = ('teacher_ID', 'class_ID')
        db_table = 'teacher_class'


class Material(models.Model):
    id = models.AutoField(primary_key=True, db_column='material_ID')
    url = models.CharField(max_length=1023, db_column='URL')
    type = models.CharField(max_length=255, db_column='type')
    explain = models.CharField(max_length=255, db_column='explain')
    class_id = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_ID')
    init_name = models.CharField(max_length=1023, db_column='init_name')

    class Meta:
        db_table = 'material'


class Sign(models.Model):
    id = models.AutoField(primary_key=True, db_column='sign_ID')
    name = models.CharField(max_length=255, db_column='name')
    classe = models.ForeignKey('Class', on_delete=models.CASCADE, db_column='class_id')
    latitude = models.CharField(max_length=255, db_column='latitude')
    longitude = models.CharField(max_length=255, db_column='longitude')
    time = models.CharField(max_length=255, db_column='time')
    threshold_minutes = models.CharField(max_length=255, db_column='threshold_minutes')

    class Meta:
        db_table = 'Sign'


class StudentSign(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')
    sign = models.ForeignKey('Sign', on_delete=models.CASCADE, db_column='sign_ID')
    state = models.BooleanField(db_column='state')
    message = models.TextField(max_length=4096, db_column='message')

    class Meta:
        db_table = 'StudentSign'

class HomeworkFile(models.Model):
    ID = models.AutoField(primary_key=True, db_column='file_id')
    URL = models.CharField(max_length=1024, db_column='file_url')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, db_column='student_ID')
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE, db_column='homework_ID')
    init_name = models.CharField(max_length=1024, db_column='init_name')
    type = models.CharField(max_length=128, db_column='file_type')

    class Meta:
        db_table = 'HomeworkFile'
