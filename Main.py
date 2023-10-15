import datetime
import hashlib
import hmac
import json
import random
import sys
import time

import requests
from tqdm import tqdm

from utils import MessagePush

SECRET_KEY = 'Anything_2023'
ADDITIONAL_TEXT = None
DTYPE = 6


def get_token():
    global ADDITIONAL_TEXT
    if ADDITIONAL_TEXT:
        return ADDITIONAL_TEXT
    url = "https://sxbaapp.vae.ha.cn/interface/token.ashx"
    headers = {
        'content-type': 'application/json;charset=UTF-8',
    }
    response = requests.post(url, headers=headers)
    try:
        result = response.json()
        if result["code"] == 1001:
            token = result["data"]["token"]
            return token
        else:
            return ""
    except json.JSONDecodeError:
        return ""


def load_users_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        users = json.load(file)
    return users


def calculate_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def calculate_hmac_sha256(secret_key, message):
    key = bytes(secret_key, 'utf-8')
    message = bytes(message, 'utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    return hashed.hexdigest()


def generate_headers(sign, phone_phonetype):
    if "IPHONE" and "iPhone" and "iphone" in phone_phonetype:
        os = "android"
    else:
        os = "ios"
    return {
        'os': os,
        'phone': phone_phonetype,
        'appversion': '56',
        'sign': sign,
        'content-type': 'application/json;charset=UTF-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.14.9'
    }


def send_request(url, method, headers, data):
    if method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=data)
    else:
        raise ValueError("Unsupported HTTP method")
    return response.text


def calculate_sign(data, additional_text, secret_key=SECRET_KEY):
    json_data = json.dumps(data)
    combined_text = json_data + additional_text
    return calculate_hmac_sha256(secret_key, combined_text)


def login_request(phone_number, password, dToken, additional_text):
    data = {
        "phone": phone_number,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "dtype": 6,
        "dToken": dToken
    }
    sign = calculate_sign(data, additional_text)
    headers = generate_headers(sign, phone_number)
    url = 'http://sxbaapp.vae.ha.cn/interface/relog.ashx'
    response_text = send_request(url, 'POST', headers, data)
    return response_text


def sign_in_request(uid, address, phonetype, probability, longitude, latitude, additional_text,
                    modify_coordinates=False):
    longitude = float(longitude)
    latitude = float(latitude)
    if modify_coordinates:
        longitude = round(longitude + random.uniform(-0.00001, 0.00001), 6)
        latitude = round(latitude + random.uniform(-0.00001, 0.00001), 6)
    data = {
        "dtype": 1,
        "uid": uid,
        "address": address,
        "phonetype": phonetype,
        "probability": probability,
        "longitude": longitude,
        "latitude": latitude
    }
    sign = calculate_sign(data, additional_text)
    headers = generate_headers(sign, phonetype)
    url = 'http://sxbaapp.vae.ha.cn/interface/clockindaily20220827.ashx'
    response_text = send_request(url, 'POST', headers, data)

    return response_text


def login_and_sign_in(user, endday):
    title = "职教家园打卡失败！"
    login_feedback = "登录失败！"
    push_feedback = "推送无效！"
    # 登录
    if not user['enabled']:
        feedback = f"{user['name']} 未启用打卡，即将跳过！"
        return login_feedback, feedback, push_feedback
    if endday >= 0:
        pass
    else:
        title = "职教家园打卡通知"
        content = f"{user['name']}，您已到期！"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback
    ADDITIONAL_TEXT = get_token()
    if not ADDITIONAL_TEXT:
        title = "职教家园打卡失败！"
        content = f"{user['name']}，获取 Token 失败，无法继续操作" + f"\n剩余：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback
    login_response = login_request(user['phone'], user['password'], user['dToken'], ADDITIONAL_TEXT)
    try:
        login_result = json.loads(login_response)
        if login_result['code'] == 1001:
            uid = login_result['data']['uid']
            login_feedback = f"{user['name']} 登录成功，手机号：{user['phone']}，UID:{uid}"
            time.sleep(1)
            sign_in_response = sign_in_request(uid, user['address'], user['deviceId'], 2, user['longitude'],
                                               user['latitude'], ADDITIONAL_TEXT,
                                               user['modify_coordinates'])
            try:
                sign_in_result = json.loads(sign_in_response)
                if sign_in_result['code'] == 1001:
                    title = "职教家园打卡成功！"
                    content = f"{user['name']}，打卡成功:" + sign_in_result['msg'] + f"\n剩余：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content, )
                    feedback = content
                    return login_feedback, feedback, push_feedback
                else:
                    content = f"{user['name']}，打卡失败，错误信息:" + sign_in_result.get('msg',
                                                                                        '未知错误') + f"\n剩余：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content)
                    feedback = content
                    return login_feedback, feedback, push_feedback
            except json.JSONDecodeError:
                content = f"{user['name']}，处理打卡响应时发生 JSON 解析错误" + f"\n剩余：{endday}天"
                push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"],
                                                        pushdata=user['pushdata'], title=title, content=content)
                feedback = content
                return login_feedback, feedback, push_feedback
        else:
            content = f"{user['name']}，登录失败，错误信息:" + login_result.get('msg', '未知错误') + f"\n剩余：{endday}天"
            push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                    title=title, content=content)
            feedback = content
            return login_feedback, feedback, push_feedback
    except json.JSONDecodeError:
        content = f"{user['name']}，处理登录响应时发生 JSON 解析错误" + f"\n剩余：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback
    except KeyError:
        content = f"{user['name']}，处理登录响应时发生关键字错误" + f"\n剩余：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback


if __name__ == "__main__":
    print("项目免费开源，详情见：https://github.com/zycn0910/Sign-ZXJY")
    waittime = 2
    users_file_path = "all-users.json"
    users = load_users_from_json(users_file_path)
    with tqdm(users, desc=f"打卡", total=len(users), unit="人", colour="#00FF00", ncols=100, leave=True, position=0,
              file=sys.stdout) as bar:
        for user in bar:
            time.sleep(waittime)
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(user['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            info = login_and_sign_in(user=user, endday=TDOA.days)
            for i in range(0, len(info)):
                tqdm.write(f"{info[i]}")
                i = i + 1
            tqdm.write("====================")
        bar.close()
