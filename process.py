import datetime
import hashlib
import hmac
import json
import logging
import os
import random
import re
import time
import requests
import yaml

from chinese_calendar import get_holiday_detail
from openai import OpenAI
from utils import MessagePush

# 读取配置文件config.yml并转化为json格式
with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

# 是否开启日志
if config['log_report']:
    log_file_Name = f"职教家园-{datetime.datetime.now().strftime('%Y-%m-%d %H')}.log"
    if not os.path.exists("log"):
        os.mkdir("log")
    else:
        pass
    open(f"log/{log_file_Name}", "a")
    logging.getLogger('DEBUG')
    logging.basicConfig(level=logging.NOTSET,
                        filename=f"log/{log_file_Name}",
                        filemode="a",
                        format="%(asctime)s - %(name)s - %(levelname)-s - %(message)s - %(filename)s - %(funcName)s - %(lineno)s",
                        datefmt="%Y-%m-%d %H:%M:%S")
else:
    pass


# 获取配置文件内随机时间
def random_Time(time):
    time = time.split("-")
    data = random.randint(int(time[0]), int(time[1]))
    logging.info(data)
    return data


# 从all-users.json内遍历用户数据
def load_users_from_json(file_path):
    if os.path.exists(file_path):
        logging.info("检测到用户数据文件，已加载！")
    else:
        open(file_path, 'w', encoding='utf-8').write("[\n\n]")
        logging.info(f"未检测到 {file_path} 文件，已自动创建！")
    return json.load(open(file_path, 'r', encoding='utf-8'))


# ZXJY加盐加密方式
def calculate_hmac_sha256(secret_key, message):
    key = bytes(secret_key, 'utf-8')
    message = bytes(message, 'utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    logging.info(hashed)
    return hashed.hexdigest()


# 请求头生成
def generate_headers(sign, phonetype, token):
    if "iph" in phonetype.lower():
        os = "ios"
        Accept = "*/*"
        Version = "".join(re.findall('new__latest__version">(.*?)</p>',
                                     requests.get(
                                         'https://apps.apple.com/us/app/%E8%81%8C%E6%A0%A1%E5%AE%B6%E5%9B%AD/id1606842290').text,
                                     re.S)).replace('Version ', '')
        Accept_Encoding = 'gzip, deflate, br'
        Accept_Language = 'zh-Hans-CN;q=1'
        Content_Type = 'application/json;charset=UTF-8'
        User_Agent = "Internship/1.4.3 (iPhone; iOS 16.7.2; Scale/3.00)"
        Connection = "keep-alive"
    else:
        os = "android"
        Accept = "*/*"
        Version = "".join(re.findall('v\d+\.\d+\.\d+',
                                     requests.get(
                                         'https://r.app.xiaomi.com/details?id=com.wyl.exam').text,
                                     re.S)).replace('v', '')
        Accept_Encoding = 'gzip'
        Accept_Language = 'zh-Hans-CN;q=1'
        Content_Type = 'application/json; charset=UTF-8'
        User_Agent = "okhttp/3.14.9"
        Connection = "keep-alive"
    data = {
        'Accept': Accept,
        'timestamp': str(int(time.time() * 1000)),
        "cl_ip": f"192.168.{range(0, 255)}.{range(0, 255)}",
        'os': os,
        'Accept-Encoding': Accept_Encoding,
        'Accept-Language': Accept_Language,
        'Content-Type': Content_Type,
        'User-Agent': User_Agent,
        'Connection': Connection,
        'phone': phonetype,
        'token': token,
        'Sign': sign,
        'appVersion': Version
    }
    logging.info(data)
    return data


# 获取登录api_token
def get_Apitoken():
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/getApitoken.ashx"
    headers = {
        'content-type': 'application/json;charset=UTF-8',
        'User-Agent': 'Internship/1.3.8 (iPhone; iOS 16.6; Scale/3.00)'
    }
    response = json.loads(send_request(url=url, method='POST', headers=headers, data=None))
    if response["code"] == 1001:
        token = response["data"]["apitoken"]
        logging.info(token)
        return True, token
    else:
        logging.info("get_Apitoken获取token失败")
        return False


# 请求发送函数
def send_request(url, method, headers, data):
    if method.upper() == 'POST':
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        return response.text
    elif method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=data)
        return response.text
    else:
        raise ValueError("Unsupported HTTP method")


# ZXJY请求头内sign加密方式
def calculate_sign(data, token):
    json_data = json.dumps(data)
    combined_text = json_data + token
    data = calculate_hmac_sha256('Anything_2023', combined_text)
    logging.info(data)
    return data


# ZXJY打卡函数
def sign_in_request(uid, address, phonetype, probability, longitude, latitude, token,
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
    sign = calculate_sign(data, token)
    header = generate_headers(sign, phonetype, token)
    url = 'https://sxbaapp.zcj.jyt.henan.gov.cn/api/clockindaily20220827.ashx'
    response_text = json.loads(send_request(url=url, method='POST', headers=header, data=data))
    logging.info(response_text)
    if response_text['code'] == 1001:
        return True, response_text['msg']
    else:
        return False, response_text['msg']


# 获取ZXJY用户信息
def get_user_info(uid, deviceId, token):
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/relog.ashx"
    data = {
        "dtype": 2,
        "uid": uid
    }
    sign = calculate_sign(data, token)
    header = generate_headers(sign, deviceId, token)
    user_info = json.loads(send_request(url=url, method='POST', headers=header, data=data))
    logging.info(user_info)
    if user_info['code'] == 1001:
        return True, user_info['data']['uname'], user_info['data']['major']
    else:
        return False


# 获取ZXJY用户数据
def get_account_data(phone, password, deviceId):
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/relog.ashx"
    data = {
        "dtype": 6,
        "phone": phone,
        'password': hashlib.md5(password.encode()).hexdigest(),
    }
    token = get_Apitoken()[1]
    sign = calculate_sign(data, token)
    header = generate_headers(sign, deviceId, token)
    account_data = json.loads(send_request(url=url, method='POST', headers=header, data=data))
    logging.info(account_data)
    if account_data['code'] == 1001:
        return True, account_data['data']['uid'], account_data['data']['UserToken']
    else:
        return account_data['msg']


# 获取ZXJY用户岗位信息
def get_job_data(uid, deviceId, token):
    data = {
        "dtype": 1,
        "uid": uid
    }
    sign = calculate_sign(data, token)
    headers = generate_headers(sign, deviceId, token)
    url = "https://sxbaapp.zcj.jyt.henan.gov.cn/api/shixi_student_check.ashx"
    job_data = json.loads(send_request(url, 'POST', headers, data))
    logging.info(job_data)
    if job_data['code'] == 1001:
        return True, job_data['data']['bmlist'][0]['gwName']
    else:
        return False


# ZXJY打卡函数调用
def login_and_sign_in(user, endday):
    title = "职教家园打卡通知"
    login_feedback = "登录失败！"
    push_feedback = "推送无效！"
    if not user['enabled']:
        content = f"未启用打卡，即将跳过！"
        return login_feedback, content, push_feedback
    if endday >= 0:
        pass
    else:
        content = f"您已到期！"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        return login_feedback, content, push_feedback
    if config['holiday_pass']:
        holiday_data = get_holiday_detail(datetime.date(2024, 5, 1))
        if holiday_data:
            if holiday_data[1] is None:
                content = f'{user["name"]}，今天是法定节假日！无需打卡！\n剩余时间：{endday}天'
            else:
                content = f'{user["name"]}，今天是 {holiday_data[1]} ！，无需打卡！\n剩余时间：{endday}天'
            push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                    pushdata=user['pushdata'], title=title, content=content)
            return login_feedback, content, push_feedback
        else:
            pass
    try:
        account_data = get_account_data(user['phone'], user['password'], user['deviceId'])
        if account_data:
            login_feedback = f"{user['name']}，登录成功！"
            uid = account_data[1]
            token = account_data[2]
            if not token:
                print("获取 Token 失败，无法继续操作")
            sign_in_response = sign_in_request(uid, user['address'], user['deviceId'], 0, user['longitude'],
                                               user['latitude'], token,
                                               user['modify_coordinates'])
            if sign_in_response[0]:
                title = "职教家园打卡成功！"
                content = f"{user['name']}，打卡成功！\n提示信息：" + sign_in_response[1]
                if config['day_report'] or config['week_report'] or config['month_report']:
                    content = content + f"\n实习报告提交：{report_handler(user, uid, token)}" + f"\n剩余时间：{endday}天"
            else:
                content = f"{user['name']}，打卡失败！\n错误信息：" + sign_in_response[1] + f"\n剩余时间：{endday}天"
        else:
            content = f"{user['name']}，登录失败！\n错误信息：" + '获取uid和token失败！' + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                pushdata=user['pushdata'], title=title, content=content)
        return login_feedback, content, push_feedback
    except Exception as e:
        content = f"{user['name']}，{e}" + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        return login_feedback, content, push_feedback


# GPT提示词生成
def prompt_handler(step, speciality=None, job=None, types=None, plan=None, data=None):
    if step == 'first':
        return f'我是{speciality}专业的实习生，根据我的专业和我的工作{job}，写一份实习计划，要求：100字以内。'
    if step == 'second':
        return f'我将给你一份实习计划：{plan}，根据此计划写一份实习{types}，要求100字以内，包含项目名字（不包含我的专业名字），项目记录，项目总结，并以json格式输出。'
    if step == 'third':
        return f'我将给你一份数据{data}，请根据json格式处理给我，格式要求只包含：项目名字（project），项目记录（record），项目总结（summary），不要输出其他多余内容。'


# GPT处理函数
def gpt_handler(prompt):
    if config['gpt_data']['key'] is None:
        logging.info('GPT-key未配置')
        return False, 'GPT-key未配置'
    if config['gpt_data']['url'] is None:
        client = OpenAI(
            api_key=config['gpt_data']['key']
        )
    else:
        client = OpenAI(
            base_url=config['gpt_data']['url'],
            api_key=config['gpt_data']['key']
        )
    messages = [{"role": "user", "content": prompt}]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            temperature=0.7,
        )
        logging.info(response)
        return True, response.choices[0].message.content
    except Exception as e:
        logging.info(e)
        return False, e


# 提交日报
def day_Report(time, user, uid, token, summary, record, project):
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
    sign = calculate_sign(data, token)
    header = generate_headers(sign, user['deviceId'], token)
    info = send_request(url=url, method='POST', headers=header, data=data)
    logging.info(info)
    return json.loads(info)


# 提交周报
def week_Report(time, user, uid, token, summary, record, project):
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
    sign = calculate_sign(data, token)
    header = generate_headers(sign, user['deviceId'], token)
    info = send_request(url=url, method='POST', headers=header, data=data)
    logging.info(info)
    return info


# 提交月报
def month_Report(time, user, uid, token, summary, record, project):
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
    sign = calculate_sign(data, token)
    header = generate_headers(sign, user['deviceId'], token)
    info = send_request(url=url, method='POST', headers=header, data=data)
    logging.info(info)
    return info


# 报告提交调用
def report_handler(user, uid, token):
    speciality = get_user_info(uid, user['deviceId'], token)[2]
    job = get_job_data(uid, user['deviceId'], token)[1]
    content = ''
    if get_holiday_detail(datetime.datetime.now().date()):
        content = '今日为法定节假日！暂未提交报告！'
        return content
    if config['day_report']:
        first_prompt = prompt_handler(step='first', speciality=speciality, job=job)
        logging.info(first_prompt)
        first_gpt = gpt_handler(first_prompt)
        logging.info(first_gpt)
        second_prompt = prompt_handler(step='second', speciality=speciality, job=job, types='日报', plan=first_gpt)
        logging.info(second_prompt)
        second_gpt = gpt_handler(second_prompt)
        logging.info(second_gpt)
        third_prompt = prompt_handler(step='third', data=second_gpt)
        third_gpt = gpt_handler(third_prompt)
        this_day_report_data = json.loads(third_gpt[1])
        this_day_result = day_Report(datetime.datetime.now(), user,
                                     uid,
                                     token,
                                     this_day_report_data['summary'],
                                     this_day_report_data['record'],
                                     this_day_report_data['project'])
        try:
            content = content + '\n日报：' + f"{this_day_result['msg']}\n{this_day_report_data['project']}\n{this_day_report_data['record']}\n{this_day_report_data['summary']}"
        except Exception as e:
            this_day_result_content = this_day_result
            logging.warning(e)
            logging.info(this_day_result_content)
    if config['week_report']:
        if datetime.datetime.weekday(datetime.datetime.now()) == 0:
            first_prompt = prompt_handler(step='first', speciality=speciality, job=job)
            logging.info(first_prompt)
            first_gpt = gpt_handler(first_prompt)
            logging.info(first_gpt)
            second_prompt = prompt_handler(step='second', speciality=speciality, job=job, types='周报', plan=first_gpt)
            logging.info(second_prompt)
            second_gpt = gpt_handler(second_prompt)
            logging.info(second_gpt)
            third_prompt = prompt_handler(step='third', data=second_gpt)
            logging.info(third_prompt)
            third_gpt = gpt_handler(third_prompt)
            logging.info(third_gpt)
            this_week_report_data = json.loads(third_gpt[1])
            this_week_result = week_Report(datetime.datetime.now(), user,
                                           uid,
                                           token,
                                           this_week_report_data['summary'],
                                           this_week_report_data['record'],
                                           this_week_report_data['project'])
            try:
                content = content + '\n周报：' + f"{this_week_result['msg']}\n{this_week_report_data['project']}\n{this_week_report_data['record']}\n{this_week_report_data['summary']}"
            except Exception as e:
                this_week_result_content = this_week_result
                logging.warning(e)
                logging.info(this_week_result_content)
    if config['month_report']:
        if datetime.datetime.now().strftime("%d") == "25":
            first_prompt = prompt_handler(step='first', speciality=speciality, job=job)
            logging.info(first_prompt)
            first_gpt = gpt_handler(first_prompt)
            logging.info(first_gpt)
            second_prompt = prompt_handler(step='second', speciality=speciality, job=job, types='月报', plan=first_gpt)
            logging.info(second_prompt)
            second_gpt = gpt_handler(second_prompt)
            logging.info(second_gpt)
            third_prompt = prompt_handler(step='third', data=second_gpt)
            logging.info(third_prompt)
            third_gpt = gpt_handler(third_prompt)
            logging.info(third_gpt)
            this_month_report_data = json.loads(third_gpt[1])
            this_month_result = month_Report(datetime.datetime.now(), user,
                                             uid,
                                             token,
                                             this_month_report_data['summary'],
                                             this_month_report_data['record'],
                                             this_month_report_data['project'])
            try:
                content = content + '\n月报：' + f"{this_month_result['msg']}\n{this_month_report_data['project']}\n{this_month_report_data['record']}\n{this_month_report_data['summary']}"
            except Exception as e:
                this_month_result_content = this_month_result
                logging.warning(e)
                logging.info(this_month_result_content)
    logging.info(content)
    return content
