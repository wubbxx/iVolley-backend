import numpy as np
import cv2
import requests
import json_tricks as json

print("-------------开始运行AI算法-------------")
video_url ='/home/liuyuheng/video/1688096253.jpg'
service_url = 'http://localhost:5000/cv'
response = requests.post(service_url, json=video_url)
result = response.json()['attributes']
print(result['code'])
print(result['message'])
print(type(result['data']))
images = np.array(json.loads(result['data'])[0], dtype=np.uint8)
#print(images.shape)
res_url = '/home/liuyuheng/img/test.jpg'
cv2.imwrite(res_url, images)
