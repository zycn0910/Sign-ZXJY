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
import tqdm
import yaml

from lxml import etree

from utils import MessagePush

with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

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
                        datefmt="%Y-%m-%d %H:%M:%S",
                        encoding="utf-8"
                        )
else:
    pass


def get_proxy():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    page = 1
    while True:
        try:
            url = f"http://www.zdaye.com/free/{page}/"
            response = requests.get(url=url, headers=headers)
        except Exception as e:
            return None
        tree = etree.HTML(response.text)
        data = tree.xpath('//*[@id="ipc"]/tbody/tr')
        if not data:
            return False
        for i in data:
            ip = i.xpath("./td[1]/text()")[0]
            port = i.xpath("./td[2]/text()")[0]
            proxy = ip + ":" + port
            if check_proxy_alive(proxy):
                return proxy
            else:
                continue
        page = page + 1


def check_proxy_alive(proxy):
    try:
        response = requests.get('http://token.ip.api.useragentinfo.com/json?token=ab28a017dc0b7536f452fd951aed51d2',
                                proxies={'http': 'http://' + proxy}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, proxy, data
        else:
            return False
    except Exception as e:
        return False


if config['proxy_enable']:
    print("代理已开启，正在获取代理地址。。。")
    proxy_data = get_proxy()
    if proxy_data:
        logging.info(proxy_data)
        print(f"本次运行使用代理 \033[31m{proxy_data}\033[0m")
    else:
        proxy_data = None
        print("\033[31m无法从代理网站获取数据！\033[0m")
else:
    proxy_data = None


def random_Time(time):
    time = time.split("-")
    data = random.randint(int(time[0]), int(time[1]))
    logging.info(data)
    return data


def load_users_from_json(file_path):
    if os.path.exists(file_path):
        logging.info("检测到用户数据文件，已加载！")
    else:
        open(file_path, 'w', encoding='utf-8').write("[\n\n]")
        logging.info(f"未检测到 {file_path} 文件，已自动创建！")
    return json.load(open(file_path, 'r', encoding='utf-8'))


def calculate_hmac_sha256(secret_key, message):
    key = bytes(secret_key, 'utf-8')
    message = bytes(message, 'utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    logging.info(hashed)
    return hashed.hexdigest()


def generate_headers(sign, phonetype, token, timestamp):
    if "iph" in phonetype.lower():
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
    logging.info(data)
    return data


def get_Apitoken():
    url = "http://sxbaapp.zcj.jyt.henan.gov.cn/api/getApitoken.ashx"
    headers = {
        'content-type': 'application/json;charset=UTF-8',
        'User-Agent': 'Internship/1.3.8 (iPhone; iOS 16.6; Scale/3.00)'
    }
    response = requests.post(url, headers=headers)
    try:
        result = response.json()
        if result["code"] == 1001:
            token = result["data"]["apitoken"]
            logging.info(token)
            return token
        else:
            logging.info("get_Apitoken获取token失败")
            return ""
    except Exception as e:
        logging.info(e)
        return ""


def send_request(url, method, headers, data, proxy=None, content=None):
    global proxy_data
    if proxy is not None:
        if method.upper() == 'POST':
            check_proxy = check_proxy_alive(proxy)
            if check_proxy:
                tqdm.tqdm.write(
                    f"\033[33m{content}\033[0m 使用代理为：\033[32m{check_proxy[1]}\033[0m，归属地为：\033[32m{check_proxy[2]['province'] + check_proxy[2]['city']}\033[0m")
                response = requests.post(url=url, headers=headers, data=json.dumps(data),
                                         proxies={'http': 'http://' + proxy},
                                         timeout=5)
            else:
                response = requests.post(url=url, headers=headers, data=json.dumps(data))
                tqdm.tqdm.write(f"\033[31m原代理已失效\033[0m")
                tqdm.tqdm.write(f"\033[33m本次提交将不使用代理\033[0m")
                proxy_data = get_proxy()
                tqdm.tqdm.write(f"现用代理改为 \033[32m{proxy_data}\033[0m")
            logging.info(proxy)
            logging.info(response)
            return response.text
        elif method.upper() == 'GET':
            if check_proxy_alive(proxy):
                response = requests.get(url, headers=headers, params=data,
                                        proxies={'http': 'http://' + proxy},
                                        timeout=5)
            else:
                tqdm.tqdm.write(f"\033[31m原代理已失效\033[0m")
                tqdm.tqdm.write(f"\033[33m本次提交将不使用代理\033[0m")
                response = requests.get(url=url, headers=headers, data=json.dumps(data))
                proxy_data = get_proxy()
                tqdm.tqdm.write(f"现用代理改为 \033[32m{proxy_data}\033[0m")
            logging.info(proxy)
            logging.info(response)
            return response.text
        else:
            raise ValueError("Unsupported HTTP method")
    else:
        if method.upper() == 'POST':
            response = requests.post(url=url, headers=headers, data=json.dumps(data))
            return response.text
        elif method.upper() == 'GET':
            response = requests.get(url=url, headers=headers, data=json.dumps(data))
            return response.text
        else:
            raise ValueError("Unsupported HTTP method")


def calculate_sign(data, token):
    json_data = json.dumps(data)
    combined_text = json_data + token
    data = calculate_hmac_sha256('Anything_2023', combined_text)
    logging.info(data)
    return data


def login_request(phone_type, phone_number, password, additional_text=None, data=None):
    if data is None:
        data = {
            "phone": phone_number,
            "password": hashlib.md5(password.encode()).hexdigest(),
            "dtype": 6,
        }
    sign = calculate_sign(data, additional_text)
    headers = generate_headers(sign, phone_type, additional_text, str(round(time.time() * 1000)))
    url = 'http://sxbaapp.zcj.jyt.henan.gov.cn/api/relog.ashx'
    content = "登录请求"
    response_text = send_request(url=url, method='POST', headers=headers, data=data, proxy=proxy_data, content=content)
    logging.info(response_text)
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
    header = generate_headers(sign, phonetype, additional_text, str(round(time.time() * 1000)))
    url = 'http://sxbaapp.zcj.jyt.henan.gov.cn/api/clockindaily20220827.ashx'
    content = "签到请求"
    response_text = send_request(url=url, method='POST', headers=header, data=data, proxy=proxy_data, content=content)
    logging.info(response_text)
    return response_text


def get_user_uid(deviceId, phone, password):
    login_token = get_Apitoken()
    if not login_token:
        print("获取 Token 失败，无法继续操作")
    login_data = login_request(deviceId, phone, password, login_token)
    logging.info(login_data)
    return login_data


def get_account_data(deviceId, phone, password):
    user_data = json.loads(get_user_uid(deviceId, phone, password))
    uid = user_data['data']['uid']
    data = {
        "dtype": 2,
        "uid": uid
    }
    login_data = login_request(deviceId, phone, password, user_data['data']['UserToken'], data)
    logging.info(login_data)
    return login_data


def login_and_sign_in(user, endday):
    title = "职教家园打卡失败！"
    login_feedback = "登录失败！"
    push_feedback = "推送无效！"
    # 登录
    if not user['enabled']:
        content = f"未启用打卡，即将跳过！"
        data = login_feedback, content, push_feedback
        logging.info(data)
        return data
    if endday >= 0:
        pass
    else:
        title = "职教家园打卡通知"
        content = f"您已到期！"
        push_feedback = MessagePush.pushMessage(addinfo=True, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        data = login_feedback, content, push_feedback
        logging.info(data)
        return data
    login_data = get_user_uid(user['deviceId'], user['phone'], user['password'])
    try:
        login_result = json.loads(login_data)
        if login_result['code'] == 1001:
            login_feedback = f"{user['name']} 登录成功！"
            uid = login_result['data']['uid']
            global ADDITIONAL_TEXT
            ADDITIONAL_TEXT = login_result['data']['UserToken']
            if not ADDITIONAL_TEXT:
                print("获取 Token 失败，无法继续操作")
            sign_in_response = sign_in_request(uid, user['address'], user['deviceId'], 0, user['longitude'],
                                               user['latitude'], ADDITIONAL_TEXT,
                                               user['modify_coordinates'])
            logging.info(sign_in_response)
            try:
                sign_in_result = json.loads(sign_in_response)
                if sign_in_result['code'] == 1001:
                    title = "职教家园打卡成功！"
                    content = f"打卡成功，提示信息：" + sign_in_result['msg']
                    if config['day_report'] or config['week_report'] or config['month_report']:
                        content = content + f"\n实习报告提交：{report_handler(user)}" + f"\n剩余时间：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content, )
                    logging.info(f"{login_feedback}, {content}, {push_feedback}")
                    return login_feedback, content, push_feedback
                else:
                    content = f"打卡失败，错误信息：" + sign_in_result.get('msg',
                                                                         '未知错误') + f"\n剩余时间：{endday}天"
                    push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                            pushdata=user['pushdata'], title=title, content=content)
                    logging.info(f"{login_feedback}, {content}, {push_feedback}")
                    return login_feedback, content, push_feedback
            except json.JSONDecodeError:
                content = f"处理打卡响应时发生 JSON 解析错误" + f"\n剩余时间：{endday}天"
                push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"],
                                                        pushdata=user['pushdata'], title=title, content=content)
                logging.info(f"{login_feedback}, {content}, {push_feedback}")
                return login_feedback, content, push_feedback
        else:
            content = f"登录失败，错误信息：" + login_result.get('msg', '未知错误') + f"\n剩余时间：{endday}天"
            push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                    title=title, content=content)
            logging.info(f"{login_feedback}, {content}, {push_feedback}")
            return login_feedback, content, push_feedback
    except json.JSONDecodeError:
        content = f"处理登录响应时发生 JSON 解析错误" + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        logging.info(f"{login_feedback}, {content}, {push_feedback}")
        return login_feedback, content, push_feedback
    except KeyError:
        content = f"处理登录响应时发生关键字错误" + f"\n剩余时间：{endday}天"
        push_feedback = MessagePush.pushMessage(addinfo=False, pushmode=user["pushmode"], pushdata=user['pushdata'],
                                                title=title, content=content)
        logging.info(content)
        return login_feedback, content, push_feedback


def day_Report(time, user, uid, summary, record, project):
    url = "http://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
    data = {
        "address": user['address'],
        "uid": uid,
        "summary": summary,
        "record": record,
        "starttime": time.strftime("%Y-%m-%d"),
        "dtype": 1,
        "project": project
    }
    sign = calculate_sign(data, ADDITIONAL_TEXT)
    header = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT, str(round(time.time() * 1000)))
    content = "日报请求"
    info = send_request(url=url, method='POST', headers=header, data=data, proxy=proxy_data, content=content)
    logging.info(info)
    return json.loads(info)


def week_Report(time, user, uid, summary, record, project):
    url = "http://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
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
    header = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT, str(round(time.time() * 1000)))
    content = "周报请求"
    info = send_request(url=url, method='POST', headers=header, data=data, proxy=proxy_data, content=content)
    logging.info(info)
    return info


def month_Report(time, user, uid, summary, record, project):
    url = "http://sxbaapp.zcj.jyt.henan.gov.cn/api/ReportHandler.ashx"
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
    header = generate_headers(sign, user['deviceId'], ADDITIONAL_TEXT, str(round(time.time() * 1000)))
    content = "月报请求"
    info = send_request(url=url, method='POST', headers=header, data=data, proxy=proxy_data, content=content)
    logging.info(info)
    return info


def load_report_data_from_json(file_path):
    if os.path.exists(file_path):
        logging.info("检测到实习报告文件，已加载！")
    else:
        open(file_path, 'w', encoding='utf-8').write("[\n\n]")
        logging.info(f"未检测到 {file_path} 文件，已自动创建！")
    return json.load(open(file_path, 'r', encoding='utf-8'))


def report_handler(user):
    if config['day_report']:
        day_report_data = load_users_from_json("day_report.json")
        this_day_report_data = day_report_data[random.randint(0, (len(day_report_data) - 1))]
        this_day_result = day_Report(datetime.datetime.now(), user,
                                     json.loads(get_user_uid(user['deviceId'], user['phone'], user['password']))[
                                         'data']['uid'],
                                     this_day_report_data['summary'],
                                     this_day_report_data['recored'],
                                     this_day_report_data['project'])
        try:
            this_day_result_content = f"{this_day_result['msg']}"
        except:
            this_day_result_content = this_day_result
            logging.info(this_day_result_content)
        return this_day_result_content
    if config['week_report']:
        if datetime.datetime.weekday(datetime.datetime.now()) == 6:
            week_report_data = load_users_from_json("week_report.json")
            this_week_report_data = week_report_data[random.randint(0, (len(week_report_data) - 1))]
            this_week_result = day_Report(datetime.datetime.now(), user,
                                          json.loads(get_user_uid(user['deviceId'], user['phone'], user['password']))[
                                              'data']['uid'],
                                          this_week_report_data['summary'],
                                          this_week_report_data['recored'],
                                          this_week_report_data['project'])
            try:
                this_week_result_content = f"{this_week_result['msg']}"
            except:
                this_week_result_content = this_week_result
                logging.info(this_week_result_content)
            return this_week_result_content
    if config['month_report']:
        if datetime.datetime.now().strftime("%m") == "30":
            month_report_data = load_report_data_from_json("month_report.json")
            this_month_report_data = month_report_data[random.randint(0, (len(month_report_data) - 1))]
            this_month_result = day_Report(datetime.datetime.now(), user,
                                           json.loads(get_user_uid(user['deviceId'], user['phone'], user['password']))[
                                               'data']['uid'],
                                           this_month_report_data['summary'],
                                           this_month_report_data['recored'],
                                           this_month_report_data['project'])
            try:
                this_month_result_content = f"{this_month_result['msg']}"
            except:
                this_month_result_content = this_month_result
                logging.info(this_month_result_content)
            return this_month_result_content
