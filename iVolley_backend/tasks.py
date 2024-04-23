from pathlib import Path

from celery import shared_task
from django.http import JsonResponse, FileResponse
import os
import requests
import numpy as np
import cv2
import json_tricks as json
import iVolley.settings as settings
from iVolley_backend.models import *

from iVolley.celery import celery_app
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

tag_dict = {
    0: '垫球',
    4: '传球',
    3: '发球',
    1: '扣球',
    2: '拦网',
    5: '其它'
}


@shared_task()
def openpose(id, file_url, type, tag):
    # 0 video / 1 img
    print("-------------开始运行AI算法-------------")
    name = (file_url.rsplit("/")[-1]).rsplit(".")[0]
    print(f"tag = {tag}")
    # 运行姿态分析算法
    # service_url = 'http://localhost:5000/cv'
    # response = requests.post(service_url, json=file_url)
    data = {
        "file_url": file_url,
        "tag": tag
    }
    # 运行姿态分析算法
    service_url = 'http://localhost:5000/cv'
    response = requests.post(service_url, json=data)
    # 获取结果
    result = response.json()['attributes']
    message = result['message']
    outputPath = result['outputPath']
    print(f"response = {response}")
    print(f"message = {message}")
    print(f"outputPath = {outputPath}")
    if outputPath is not None:
        output_base = settings.OUT_BASE_PATH + 'output/' + outputPath.rsplit('/')[-2] + "/" + outputPath.rsplit('/')[-1]
    if type == 0:
        video = Video.objects.get(ID=id)
        if outputPath is None:
            name = video.URL.rsplit("/")[-1]
            URL = settings.POST_VIDEO_PATH + name
            video.error_video = URL
            video.AI_feedback = f"暂不支持{tag_dict.get(int(tag))}类动作评判"
        elif len(message) == 0:
            video.AI_feedback = "该动作通过AI检测，为标准动作"
            name = video.URL.rsplit("/")[-1]
            URL = settings.POST_VIDEO_PATH + name
            video.error_video = URL

        else:
            video.AI_feedback = result['message']
            video.error_video = output_base
        video.AI_status = True
        video.save()
    else:
        img = Image.objects.get(ID=id)
        if outputPath is None:
            name = img.URL.rsplit("/")[-1]
            URL = settings.POST_IMG_PATH + name
            img.AI_feedback = f"暂不支持{tag_dict.get(int(tag))}类动作评判"
            img.error_img = URL
        elif len(message) == 0:
            name = img.URL.rsplit("/")[-1]
            URL = settings.POST_IMG_PATH + name
            img.error_img = URL
            img.AI_feedback = "该动作通过AI检测，为标准动作"
        else:
            img.AI_feedback = message
            img.error_img = output_base
        img.AI_status = True
        img.save()
    channels_layer = get_channel_layer()
    async_to_sync(channels_layer.group_send)('task_status_group', {
        'type': 'task_status',
        'message': 'Task name is completed.'
    })
    async_to_sync(channels_layer.group_send)('task_result_group', {
        'type': 'task_result',
        'message': 'Task result is successful.',
    })
    return None