import datetime as datetime
import json
import os
import random
import string
import time
import urllib

import requests

import config
from utils import MessagePush

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep


def write_user(filename, newdata):
    with open(filename, 'r', encoding='utf-8') as f:
        olddata = f.read()
    olddata = json.loads(olddata)
    olddata.extend(newdata)
    with open(filename, 'w', encoding='utf-8') as write_f:
        write_f.write(json.dumps(olddata, indent=2, ensure_ascii=False))


def obtain_coordinates(address):
    url = f"https://apis.map.qq.com/jsapi?qt=geoc&addr={urllib.parse.quote(address)}&key={config.api_token}&output=jsonp&pf=jsapi&ref=jsapi&cb=qq.maps._svcb3.geocoder0"
    re = requests.get(url=url).text.strip("qq.maps._svcb3.geocoder0(").strip(")")
    re = json.loads(re)
    return re['detail']['pointx'] + "@" + re['detail']['pointy']


def write_file(filename, enable, day, name, phone, password, device, modify_coordinates, address, pushmode, Ding_secret, Ding_token,
               PushPlus_token, Server_Turbo_token,
               email_username, email_password, email_address, email_port, email_receiver, check):
    adddate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    enddate = (datetime.datetime.now() + datetime.timedelta(days=float(day))).strftime("%Y-%m-%d %H:%M:%S")
    deviceID = ''.join(random.sample(string.digits + string.ascii_lowercase, 36))
    longitude = obtain_coordinates(address=address).split("@")[0]
    latitude = obtain_coordinates(address=address).split("@")[1]
    newdata = [
        {
            "enabled": enable,
            "adddate": adddate,
            "enddate": enddate,
            "name": name,
            "phone": phone,
            "password": password,
            "deviceId": device,
            "dToken": deviceID,
            "modify_coordinates": modify_coordinates,
            "address": address,
            "longitude": longitude,
            "latitude": latitude,
            "pushmode": pushmode,
            "pushdata": {
                "Ding": {
                    "Secret": Ding_secret,
                    "Token": Ding_token
                },
                "PushPlus": {
                    "Token": PushPlus_token
                },
                "Server_Turbo": {
                    "Token": Server_Turbo_token
                },
                "Email": {
                    "Send": email_username,
                    "Password": email_password,
                    "Server_Address": email_address,
                    "Smtp_Port": email_port,
                    "Receiver": email_receiver
                }
            }
        }
    ]
    while True:
        if newdata[0]['pushmode'] == 1:
            content = f"钉钉机器人\n签名：{newdata[0]['pushdata']['Ding']['Secret']}\nToken：{newdata[0]['pushdata']['Ding']['Token']}"
        elif newdata[0]['pushmode'] == 2:
            content = f"PushPlus\nToken：{newdata[0]['pushdata']['PushPlus']['Token']}"
        elif newdata[0]['pushmode'] == 3:
            content = f"Serve_Turbo\nToken：{newdata[0]['pushdata']['Server_Turbo']['Token']}"
        elif newdata[0]['pushmode'] == 4:
            email_User = newdata[0]['pushdata']['Email']['Send']
            email_Pass = newdata[0]['pushdata']['Email']['Password']
            email_Addr = newdata[0]['pushdata']['Email']['Server_Address']
            email_Port = newdata[0]['pushdata']['Email']['Smtp_Port']
            email_Rece = newdata[0]['pushdata']['Email']['Receiver']
            content = f"邮件\n用户名：{email_User}\n密码{email_Pass}\n服务器：{email_Addr}\n端口：{email_Port}\n接收地址：{email_Rece}"
        elif newdata[0]['pushmode'] == None:
            content = f"本地打印"
        print("您的信息如下：")
        print("==========")
        print(
            f"是否启用：{newdata[0]['enabled']}\n加入时间：{newdata[0]['adddate']}\n到期时间：{newdata[0]['enddate']}"
            f"姓名：{newdata[0]['name']}\n手机号：{newdata[0]['phone']}\n密码：{newdata[0]['password']}\n设备型号：{newdata[0]['deviceId']}\n设备id（随机生成）：{newdata[0]['deviceId']}"
            f"\n地址：{newdata[0]['address']}\n经度：{newdata[0]['longitude']}\n纬度：{newdata[0]['latitude']}\n推送模式：{content}")
        if check == "y":
            write_user(filename=filename, newdata=newdata)
            print("已写入！")
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(newdata[0]['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            MessagePush.pushMessage(addinfo=True, pushmode=newdata[0]["pushmode"], title='职校家园打卡添加成功！！',
                                    content=f"姓名：{newdata[0]['name']}\n手机：{newdata[0]['phone']}\n密码：{newdata[0]['password']}\n总计：{TDOA.days}天", pushdata=newdata[0]['pushdata'])

            break
        elif check == "n":
            print("取消写入")
            break
        else:
            print("输入有误！")
            break


if __name__ == '__main__':
    # 用户数据
    filename = "all-users.json"
    # 是否开启打卡
    enabled = True
    # 打卡天数
    day = "365"
    # 备注名字
    name = ""
    # 手机号/职教家园账号
    phone = ""
    # 密码
    password = ""
    # 手机型号
    device = ""
    # 随机定位（经纬度最后一位随机）
    randomLocation = True
    # 打卡地址
    address = "河南郑州"
    # 推送方式
    pushmode = 2
    # DingDingWebHook机器人推送
    Ding_secret = ""
    Ding_token = ""
    # Pushplus推送
    PushPlus_token = ""
    # 方糖酱推送
    Server_Turbo_token = ""
    # 邮箱推送
    email_username = ""
    email_password = ""
    email_address = ""
    email_port = ""
    email_receiver = ""
    # 是否写入文件
    check = "y"
    write_file(filename, enabled, day, name, phone, password, device, randomLocation, address, pushmode, Ding_secret, Ding_token,
               PushPlus_token, Server_Turbo_token,
               email_username, email_password, email_address, email_port, email_receiver, check)
