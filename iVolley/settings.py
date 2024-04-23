"""
Django settings for iVolley project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
import pymysql
pymysql.install_as_MySQLdb()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 30  # 30 MB

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(y^83aldp9(lnx5t_m*s@#if+ey-g54_w0)6)xzm6f4mr0_ouu'
# SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
# '10.134.138.253', '127.0.0.1'

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'iVolley_backend',
    'socketmodel'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'iVolley.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'iVolley.wsgi.application'
ASGI_APPLICATION = 'iVolley.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '172.17.0.1', # docker IP
        # 'HOST': '106.39.42.222',
        'PORT': '3307',
        #'USER': 'root',
        #"PASSWORD": '030110ABc',
        'USER': 'root',
        'NAME': 'iVolley',
        # 'USER': 'liuyuheng',
        'PASSWORD': '123456',
        # 'NAME': 'iVolley',
        'OPTIONS': {'charset': 'utf8'}
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

#STATIC_ROOT = 'static' 
#STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, '/static/'),
#)

IMG_PATH = "/img/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'img')
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 发送邮箱验证码
EMAIL_HOST = "smtp.163.com"     # 服务器
EMAIL_PORT = 25                 # 一般情况下都为25
EMAIL_HOST_USER = "lyh20201025@163.com"     # 账号
EMAIL_HOST_PASSWORD = "VLEHBRLAGYCJFRRV"     # （上面保存的授权码）
EMAIL_USE_TLS = True       # 一般都为False
EMAIL_FROM = "lyh20201025@163.com"      # 邮箱来自
email_title = '邮箱激活'

# Broker配置，使用Redis作为消息中间件
BROKER_URL = 'redis://127.0.0.1:6379/0'

# BACKEND配置，这里使用redis
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# 签到距离限制
VALID_DISTANCE = 20000

# 资源存储路径
# HOME_DIR = '/home/quyingbo/ivolley/back-end/'
HOME_DIR = '/home/ivolley/iVolley/back-end/'
SUB_HW_DIR = HOME_DIR + 'sub_hw/'
PUB_HW_DIR = HOME_DIR + 'pub_hw/'
POST_VIDEO_DIR = HOME_DIR + 'post_video/'
POST_IMG_DIR = HOME_DIR + 'post_img/'
ERROR_IMG_DIR = HOME_DIR + 'error_img/'
ERROR_VIDEO_DIR = HOME_DIR + 'error_video/'
USER_IMG_DIR = HOME_DIR + 'user_img/'
TECH_VIDEO_DIR = HOME_DIR + 'tech_video/'
TASK_FILE_DIR = HOME_DIR + 'task_file/'
RE_FILE_DIR = HOME_DIR + 're_file/'
TEACH_MATERIAL_DIR = HOME_DIR + 'teach_material/'

# 资源外部访问路径
OUT_BASE_PATH = 'https://ivolley.cn:8443/'
PUB_HW_PATH = OUT_BASE_PATH+'pub_hw/'
SUB_HW_PATH = OUT_BASE_PATH+'sub_hw/'
POST_VIDEO_PATH = OUT_BASE_PATH+'post_video/'
POST_IMG_PATH = OUT_BASE_PATH+'post_img/'
ERROR_IMG_PATH = OUT_BASE_PATH+'error_img/'
ERROR_VIDEO_PATH = OUT_BASE_PATH+'error_video/'
USER_IMG_PATH = OUT_BASE_PATH+'user_img/'
TECH_VIDEO_PATH = OUT_BASE_PATH+'tech_video/'
TASK_FILE_PATH = OUT_BASE_PATH+'task_file/'
RE_FILE_PATH = OUT_BASE_PATH+'re_file/'
TEACH_MATERIAL_PATH = OUT_BASE_PATH+'teach_material/'


#跨域访问设置
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ('*')

# 添加对layer的支持
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts":[('127.0.0.1', 6379)],
        },
    },
}
