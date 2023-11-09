import json

import requests as requests


api_key = "sk-buIn2OTbOsRz3KyabxEcNLiXdd1vbO3eo0cZ3ujNe7mSpNVk"
headers = {
    "Authorization": 'Bearer ' + api_key,
}
params = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": 'user',
            "content": f"你是实习生，根据物联网应用技术专业相关内容，写出一份实习报告，包含具体项目名字（10字以内），项目记录（100字以内），项目总结（50字以内），以json数据格式输出。"
        }
    ],
    "temperature": 1

}
response = requests.post(
    "https://api.chatanywhere.com.cn/v1/chat/completions",
    headers=headers,
    json=params,
    stream=False
)

res = response.json()
print(type(json.loads(res)))


