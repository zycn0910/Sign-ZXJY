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


def write_file(filename, enabled, day, name, phone, password, device, modify_coordinates, address, pushmode=None,
               Ding_secret=None, Ding_token=None,
               PushPlus_token=None, Server_Turbo_token=None,
               email_username=None, email_password=None, email_address=None, email_port=None, email_receiver=None):
    global content
    adddate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    enddate = (datetime.datetime.now() + datetime.timedelta(days=float(day))).strftime("%Y-%m-%d %H:%M:%S")
    deviceID = ''.join(random.sample(string.digits + string.ascii_lowercase, 36))
    longitude = obtain_coordinates(address=address).split("@")[0]
    latitude = obtain_coordinates(address=address).split("@")[1]
    newdata = [
        {
            "enabled": enabled,
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
        if newdata[0]['pushmode'] == "1":
            content = f"钉钉机器人\n签名：{newdata[0]['pushdata']['Ding']['Secret']}\nToken：{newdata[0]['pushdata']['Ding']['Token']}"
        elif newdata[0]['pushmode'] == "2":
            content = f"PushPlus\nToken：{newdata[0]['pushdata']['PushPlus']['Token']}"
        elif newdata[0]['pushmode'] == "3":
            content = f"Serve_Turbo\nToken：{newdata[0]['pushdata']['Server_Turbo']['Token']}"
        elif newdata[0]['pushmode'] == "4":
            if config.email_username or config.email_password or config.email_address or config.email_port == "":
                email_User = newdata[0]['pushdata']['Email']['Send']
                email_Pass = newdata[0]['pushdata']['Email']['Password']
                email_Addr = newdata[0]['pushdata']['Email']['Server_Address']
                email_Port = newdata[0]['pushdata']['Email']['Smtp_Port']
                email_Rece = newdata[0]['pushdata']['Email']['Receiver']
            else:
                email_User, email_Pass, email_Pass, email_Addr, email_Port = None, None, None, None, None
                email_Rece = newdata[0]['pushdata']['Email']['Receiver']
            content = f"邮件\n用户名：{email_User}\n密码{email_Pass}\n服务器：{email_Addr}\n端口：{email_Port}\n接收地址：{email_Rece}"
        elif newdata[0]['pushmode'] == "":
            content = f"本地打印"
        print("您的信息如下：")
        print("==========")
        print(
            f"是否启用：{newdata[0]['enabled']}\n加入时间：{newdata[0]['adddate']}\n到期时间：{newdata[0]['enddate']}"
            f"姓名：{newdata[0]['name']}\n手机号：{newdata[0]['phone']}\n密码：{newdata[0]['password']}\n设备型号：{newdata[0]['deviceId']}\n设备id（随机生成）：{newdata[0]['deviceId']}"
            f"\n地址：{newdata[0]['address']}\n经度：{newdata[0]['longitude']}\n纬度：{newdata[0]['latitude']}\n推送模式：{content}")
        write_user(filename=filename, newdata=newdata)
        print("已写入！")
        now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        TDOA = datetime.datetime.strptime(newdata[0]['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
            now_localtime, '%Y-%m-%d %H:%M:%S')
        MessagePush.pushMessage(addinfo=True, pushmode=newdata[0]["pushmode"], title='职校家园打卡添加成功！！',
                                content=f"姓名：{newdata[0]['name']}\n手机：{newdata[0]['phone']}\n密码：{newdata[0]['password']}\n总计：{TDOA.days}天",
                                pushdata=newdata[0]['pushdata'])

        break


if __name__ == '__main__':
    while True:
        # 用户数据
        filename = "all-users.json"
        # 是否开启打卡
        enabled = True
        # 打卡天数
        day = input("输入需要打卡天数：")
        # 备注名字
        name = input("输入账号备注：")
        # 手机号/职教家园账号
        phone = input("输入账号：")
        # 密码
        password = input("输入密码：")
        # 手机型号
        device = input("输入手机型号：")
        # 随机定位（经纬度最后一位随机）
        modify_coordinates = True
        # 打卡地址
        address = input("输入打卡地址：")
        # 推送方式
        pushmode = input("输入推送模式：")
        if pushmode == "1":
            Ding_secret = input("输入DingDing机器人签名：")
            Ding_token = input("输入DingDing机器人Token：")
            write_file(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                       device=device, modify_coordinates=modify_coordinates, address=address, pushmode=pushmode,
                       Ding_secret=Ding_secret, Ding_token=Ding_token)
        elif pushmode == "2":
            PushPlus_token = input("输入PushplusToken：")
            write_file(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                       device=device, modify_coordinates=modify_coordinates, address=address, pushmode=pushmode,
                       PushPlus_token=PushPlus_token)
        elif pushmode == "3":
            Server_Turbo_token = input("输入Server酱Token：")
            write_file(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                       device=device, modify_coordinates=modify_coordinates, address=address, pushmode=pushmode,
                       Server_Turbo_token=Server_Turbo_token)
        elif pushmode == "4":
            if config.email_username or config.email_password or config.email_address or config.email_port == "":
                email_username = input("输入邮件服务账号：")
                email_password = input("输入邮件服务密码：")
                email_address = input("输入邮件服务地址：")
                email_port = input("输入邮件服务端口：")
                email_receiver = input("输入接受邮件地址：")
                write_file(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                           device=device, modify_coordinates=modify_coordinates, address=address, pushmode=pushmode,
                           email_username=email_username, email_password=email_password, email_address=email_address,
                           email_port=email_port, email_receiver=email_receiver)
            else:
                email_receiver = input("输入接受邮件地址：")

        else:
            write_file(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                       device=device, modify_coordinates=modify_coordinates, address=address, pushmode=pushmode)
