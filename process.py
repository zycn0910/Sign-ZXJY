import datetime
import hashlib
import hmac
import json
import random
import re
import time
import requests
from tqdm import tqdm

import config
from utils import MessagePush


def random_Time(time):
    return random.randint(int(time[0]), int(time[1]))


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
                                     requests.get(
                                         'https://apps.apple.com/us/app/%E8%81%8C%E6%A0%A1%E5%AE%B6%E5%9B%AD/id1606842290').text,
                                     re.S)).replace('Version ', '')
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


def login_request(phone_type, phone_number, password, dToken, additional_text):
    data = {
        "phone": phone_number,
        "password": hashlib.md5(password.encode()).hexdigest(),
        "dtype": 6,
        "dToken": dToken
    }
    sign = calculate_sign(data, additional_text)
    headers = generate_headers(sign, phone_type, additional_text)
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


def get_user_uid(user):
    login_token = get_Apitoken()
    if not login_token:
        print("获取 Token 失败，无法继续操作")
    login_data = login_request(user['deviceId'], user['phone'], user['password'], user['dToken'], login_token)
    return login_data


def login_and_sign_in(user, endday):
    title = "职教家园打卡失败！"
    login_feedback = "登录失败！"
    push_feedback = "推送无效！"
    # 登录
    if not user['enabled']:
        content = f"未启用打卡，即将跳过！"
        return login_feedback, content, push_feedback
    if endday >= 0:
        pass
    else:
        title = "职教家园打卡通知"
        content = f"您已到期！"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        return login_feedback, content, push_feedback
    login_data = get_user_uid(user)
    try:
        login_result = json.loads(login_data)
        if login_result['code'] == 1001:
            login_feedback = f"{user['name']}登录成功！"
            uid = login_result['data']['uid']
            global ADDITIONAL_TEXT
            ADDITIONAL_TEXT = login_result['data']['UserToken']
            if not ADDITIONAL_TEXT:
                print("获取 Token 失败，无法继续操作")
            sign_in_response = sign_in_request(uid, user['address'], user['deviceId'], 0, user['longitude'],
                                               user['latitude'], ADDITIONAL_TEXT,
                                               user['modify_coordinates'])
            try:
                sign_in_result = json.loads(sign_in_response)
                if sign_in_result['code'] == 1001:
                    title = "职教家园打卡成功！"
                    content = f"打卡成功，提示信息：" + sign_in_result['msg']
                    if config.day_report or config.week_report or config.month_report:
                        content = content + f"\n实习报告提交：{report_handler(user)}" + f"\n剩余时间：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content, )
                    return login_feedback, content, push_feedback
                else:
                    content = f"打卡失败，错误信息：" + sign_in_result.get('msg',
                                                                                        '未知错误') + f"\n剩余时间：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content)
                    return login_feedback, content, push_feedback
            except json.JSONDecodeError:
                content = f"处理打卡响应时发生 JSON 解析错误" + f"\n剩余时间：{endday}天"
                push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                        pushdata=user['pushdata'], title=title, content=content)
                return login_feedback, content, push_feedback
        else:
            content = f"登录失败，错误信息：" + login_result.get('msg', '未知错误') + f"\n剩余时间：{endday}天"
            push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                    title=title, content=content)
            return login_feedback, content, push_feedback
    except json.JSONDecodeError:
        content = f"处理登录响应时发生 JSON 解析错误" + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        return login_feedback, content, push_feedback
    except KeyError:
        content = f"处理登录响应时发生关键字错误" + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        return login_feedback, content, push_feedback


def day_Report(time, user, uid, summary, record, project):
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
    data = {
        "address": user['address'],
        "uid": uid,
        "summary": summary,
        "record": record,
        "starttime": time.strftime("%Y-%m-%d"),
        "dtype": 1,
        "project": project
    }
    # print(data)
    sign = calculate_sign(data, ADDITIONAL_TEXT)
    herder = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT)
    info = send_request(url, "POST", herder, data)
    return json.loads(info)


def week_Report(time, user, uid, summary, record, project):
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
    data = {
        "address": user['address'],
        "uid": uid,
        "summary": summary,
        "record": record,
        "starttime": (time + datetime.timedelta(days=-7)).strftime('%Y-%m-%d'),
        "dtype": 2,
        "project": project,
        "endtime": time.strftime("%Y-%m-%d"),
        "stype": 2
    }
    sign = calculate_sign(data, ADDITIONAL_TEXT)
    herder = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT)
    info = send_request(url, "POST", herder, data)
    return info


def month_Report(time, user, uid, summary, record, project):
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
    data = {
        "address": user['address'],
        "uid": uid,
        "summary": summary,
        "record": record,
        "starttime": (time + datetime.timedelta(days=-30)).strftime('%Y-%m-%d'),
        "dtype": 2,
        "project": project,
        "endtime": time.strftime("%Y-%m-%d"),
        "stype": 3
    }
    sign = calculate_sign(data, ADDITIONAL_TEXT)
    herder = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT)
    info = send_request(url, "POST", herder, data)
    return info


def load_report_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def report_handler(user):
    if config.day_report:
        day_report_data = load_users_from_json("day_report.json")
        this_day_report_data = day_report_data[random.randint(0, (len(day_report_data) - 1))]
        this_day_result = day_Report(datetime.datetime.now(), user,
                                     json.loads(get_user_uid(user))['data']['uid'],
                                     this_day_report_data['summary'],
                                     this_day_report_data['recored'],
                                     this_day_report_data['project'])
        try:
            this_day_result_content = f"{this_day_result['msg']}"
        except:
            this_day_result_content = this_day_result
        return this_day_result_content
    if config.week_report:
        if datetime.datetime.weekday(datetime.datetime.now()) == 6:
            week_report_data = load_users_from_json("week_report.json")
            this_week_report_data = week_report_data[random.randint(0, (len(week_report_data) - 1))]
            this_week_result = day_Report(datetime.datetime.now(), user,
                                          json.loads(get_user_uid(user))['data']['uid'],
                                          this_week_report_data['summary'],
                                          this_week_report_data['recored'],
                                          this_week_report_data['project'])
            try:
                this_week_result_content = f"{this_week_result['msg']}"
            except:
                this_week_result_content = this_week_result
            return this_week_result_content
    if config.month_report:
        if datetime.datetime.now().strftime("%m") == "30":
            month_report_data = load_report_data_from_json("month_report.json")
            this_month_report_data = month_report_data[random.randint(0, (len(month_report_data) - 1))]
            this_month_result = day_Report(datetime.datetime.now(), user,
                                           json.loads(get_user_uid(user))['data']['uid'],
                                           this_month_report_data['summary'],
                                           this_month_report_data['recored'],
                                           this_month_report_data['project'])
            try:
                this_month_result_content = f"{this_month_result['msg']}"
            except:
                this_month_result_content = this_month_result
            return this_month_result_content
