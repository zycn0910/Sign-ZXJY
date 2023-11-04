import hashlib
import hmac
import json
import random
import re
import time

import requests

from utils import MessagePush


def get_Apitoken():
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/getApitoken.ashx"
    headers = {
        'content-type': 'application/json;charset=UTF-8',
    }
    response = requests.post(url, headers=headers)
    try:
        result = response.json()
        if result["code"] == 1001:
            token = result["data"]["apitoken"]
            return token
        else:
            return ""
    except json.JSONDecodeError:
        return ""


def load_users_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        users = json.load(file)
    return users


def calculate_hmac_sha256(secret_key, message):
    key = bytes(secret_key, 'utf-8')
    message = bytes(message, 'utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    return hashed.hexdigest()


def generate_headers(sign, phonetype, token):
    timestamp = str(round(time.time() * 1000))
    if "IPH" or "iPh" or "iph" in phonetype:
        os = "ios"
        Accept = "*/*"
        Version = "".join(re.findall('new__latest__version">(.*?)</p>',
                                     requests.get('https://apps.apple.com/us/app/%E8%81%8C%E6%A0%A1%E5%AE%B6%E5%9B%AD/id1606842290').text, re.S)).replace('Version ', '')
        Accept_Encoding = 'gzip, deflate, br'
        Accept_Language = 'zh-Hans-CN;q=1'
        Content_Type = 'application/json'
        User_Agent = "Internship/1.3.8 (iPhone; iOS 16.6; Scale/3.00)"
        Connection = "keep-alive"
    else:
        os = "android"
        Accept = "*/*"
        Version = "57"
        Accept_Encoding = 'gzip'
        Accept_Language = 'zh-Hans-CN;q=1'
        Content_Type = 'application/json; charset=UTF-8'
        User_Agent = "okhttp/3.14.9"
        Connection = "keep-alive"
    return {
        'Accept': Accept,
        'timestamp': timestamp,
        'os': os,
        'Accept-Encoding': Accept_Encoding,
        'Accept-Language': Accept_Language,
        'Content-Type': Content_Type,
        'User-Agent': User_Agent,
        'Connection': Connection,
        'phone': phonetype,
        'token': token,
        'sign': sign,
        'appVersion': Version
    }


def send_request(url, method, headers, data):
    if method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=data)
    else:
        raise ValueError("Unsupported HTTP method")
    return response.text


def calculate_sign(data, token):
    json_data = json.dumps(data)
    combined_text = json_data + token
    return calculate_hmac_sha256('Anything_2023', combined_text)


def login_request(phone_number, password, dToken, additional_text):
    data = {
        "phone": phone_number,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "dtype": 6,
        "dToken": dToken
    }
    sign = calculate_sign(data, additional_text)
    headers = generate_headers(sign, phone_number, additional_text)
    url = 'https://sxbaapp.zcj.jyt.henan.gov.cn/api/relog.ashx'
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
    headers = generate_headers(sign, phonetype, additional_text)
    url = 'https://sxbaapp.zcj.jyt.henan.gov.cn/api/clockindaily20220827.ashx'
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
    login_token = get_Apitoken()
    if not login_token:
        print("获取 Token 失败，无法继续操作")
    login_response = login_request(user['phone'], user['password'], user['dToken'], login_token)
    try:
        login_result = json.loads(login_response)
        if login_result['code'] == 1001:
            login_feedback = "登录成功！"
            uid = login_result['data']['uid']
            ADDITIONAL_TEXT = login_result['data']['UserToken']
            if not ADDITIONAL_TEXT:
                print("获取 Token 失败，无法继续操作")
            sign_in_response = sign_in_request(uid, user['address'], user['phonetype'], 0, user['longitude'],
                                               user['latitude'], ADDITIONAL_TEXT,
                                               user['modify_coordinates'])
            try:
                sign_in_result = json.loads(sign_in_response)
                if sign_in_result['code'] == 1001:
                    title = "职教家园打卡成功！"
                    content = f"{user['name']}，打卡成功:" + sign_in_result['msg'] + f"\n剩余：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content, )
                    feedback = content
                    return login_feedback, feedback, push_feedback
                else:
                    content = f"{user['name']}，打卡失败，错误信息:" + sign_in_result.get('msg', '未知错误') + f"\n剩余：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content)
                    feedback = content
                    return login_feedback, feedback, push_feedback
            except json.JSONDecodeError:
                content = f"{user['name']}，处理打卡响应时发生 JSON 解析错误" + f"\n剩余：{endday}天"
                push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                        pushdata=user['pushdata'], title=title, content=content)
                feedback = content
                return login_feedback, feedback, push_feedback
        else:
            content = f"{user['name']}，登录失败，错误信息:" + login_result.get('msg', '未知错误') + f"\n剩余：{endday}天"
            push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                    title=title, content=content)
            feedback = content
            return login_feedback, feedback, push_feedback
    except json.JSONDecodeError:
        content = f"{user['name']}，处理登录响应时发生 JSON 解析错误" + f"\n剩余：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback
    except KeyError:
        content = f"{user['name']}，处理登录响应时发生关键字错误" + f"\n剩余：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        feedback = content
        return login_feedback, feedback, push_feedback
