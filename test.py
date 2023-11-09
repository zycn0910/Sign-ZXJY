import requests as requests


api_key = "sk-dPjTPTjq718D0077CD4DT3BlbKFJ5c0fB2592a90406581f7"
headers = {
    "Authorization": 'Bearer ' + api_key,
}
params = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": 'user',
            "content": f"，根据网络仓库管理员和物联网应用技术，写出一份有具体项目的实习日报，包含项目名字（10字以内），项目记录（100字以内），项目总结（50字以内），以json数据格式输出。"
        }
    ]

}
response = requests.post(
    "https://aigptx.top/v1/chat/completions",
    headers=headers,
    json=params,
    stream=False
)

res = response.json()
print(res)
content = res['choices'][0]['message']['content'].strip().replace('"', '')
print(content)
