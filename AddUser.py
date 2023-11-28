import string
import urllib

from process import *
from utils import MessagePush


def write_user(filename, newdata):
    with open(filename, 'r', encoding='utf-8') as f:
        olddata = f.read()
    olddata = json.loads(olddata)
    olddata.extend(newdata)
    with open(filename, 'w', encoding='utf-8') as write_f:
        write_f.write(json.dumps(olddata, indent=2, ensure_ascii=False))


def obtain_coordinates(address):
    url = f"https://apis.map.qq.com/jsapi?qt=geoc&addr={urllib.parse.quote(address)}&key={config['api_token']}&output=jsonp&pf=jsapi&ref=jsapi&cb=qq.maps._svcb3.geocoder0"
    re = requests.get(url=url).text.strip("qq.maps._svcb3.geocoder0(").strip(")")
    re = json.loads(re)
    return re['detail']['pointx'] + "@" + re['detail']['pointy']


def checkUserData(filename, enabled, day, name, phone, password, device, modify_coordinates, address, pushmode=None,
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
    now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    TDOA = datetime.datetime.strptime(newdata[0]['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
        now_localtime, '%Y-%m-%d %H:%M:%S')
    pushFeedback = MessagePush.pushMessage(addinfo=True, title='职校家园打卡添加成功！！',
                                           content=f"姓名：{newdata[0]['name']}\n手机：{newdata[0]['phone']}\n密码：{newdata[0]['password']}\n总计：{TDOA.days}天",
                                           pushdata=newdata[0]['pushdata'], pushmode=newdata[0]['pushmode'])
    if "失败" in pushFeedback:
        feedback = "写入失败！原因：无法推送至指定的方式！"
    elif "成功" in pushFeedback:
        write_user(filename=filename, newdata=newdata)
        feedback = "写入成功！"
    else:
        feedback = "写入失败！原因未知！"
    return newdata, pushFeedback, feedback


if __name__ == '__main__':
    filename = "all-users.json"
    enabled = input("是否开启打卡y or n（默认y）：")
    if enabled == "y":
        enabled = True
    elif enabled == "n":
        enabled = False
    else:
        enabled = True
    while True:
        day = input("输入打卡天数：")
        if re.match(r"^-?\d+$", day):
            break
    # 手机型号
    device = input("输入手机型号：")
    while True:
        pattern = re.compile(r'^(13[0-9]|14[0|5|6|7|9]|15[0|1|2|3|5|6|7|8|9]|'
                             r'16[2|5|6|7]|17[0|1|2|3|5|6|7|8]|18[0-9]|'
                             r'19[1|3|5|6|7|8|9])\d{8}$')
        phone = input("输入账号：")
        if pattern.search(phone):
            break
        else:
            print(f"\033[31m手机号不正确！\033[0m")
    # 密码
    while True:
        password = input("输入密码：")
        password1 = input("输入密码：")
        if password1 == password:
            break
        else:
            print(f"\033[31m两次密码不一致！\033[0m")
    name = input("输入备注：（默认为职校家园姓名）")
    if name == "":
        name = json.loads(get_account_data(device, phone, password))['data']['uname']
    # 随机定位（经纬度最后一位随机）
    modify_coordinates = input("开启随机最后一位坐标y or n（默认y）：")
    if modify_coordinates == "y":
        modify_coordinates = True
    elif modify_coordinates == "n":
        modify_coordinates = False
    else:
        modify_coordinates = True
    # 打卡地址
    address = input("输入打卡地址：")
    # 推送方式
    pushmode = input("输入信息推送方式（默认控制台打印）：")
    if pushmode not in "1234":
        pushmode = None
        print(f"\033[33m输入无效，已设置默认！\033[0m")
    if pushmode == "1":
        Ding_secret = input("输入DingDing机器人Secret（留空则全局推送信息生效）：")
        Ding_token = input("输入DingDing机器人Token（留空则全局推送信息生效）：")
        userdata = checkUserData(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                                 device=device, modify_coordinates=modify_coordinates, address=address,
                                 pushmode=pushmode,
                                 Ding_secret=Ding_secret, Ding_token=Ding_token)
        pushmode = "钉钉WebHook机器人推送"
    elif pushmode == "2":
        PushPlus_token = input("输入PushPlus的Token（留空则全局推送信息生效）：")
        userdata = checkUserData(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                                 device=device, modify_coordinates=modify_coordinates, address=address,
                                 pushmode=pushmode,
                                 PushPlus_token=PushPlus_token)
        pushmode = "Pushplus推送"
    elif pushmode == "3":
        Server_Turbo_token = input("输入Server酱Token（留空则全局推送信息生效）：")
        userdata = checkUserData(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                                 device=device, modify_coordinates=modify_coordinates, address=address,
                                 pushmode=pushmode,
                                 Server_Turbo_token=Server_Turbo_token)
        pushmode = "Server酱"
    elif pushmode == "4":
        email_username = input("输入邮箱服务用户名（留空则全局推送信息生效）：")
        email_password = input("输入邮箱服务密码（留空则全局推送信息生效）：")
        email_address = input("输入邮箱服务地址（留空则全局推送信息生效）：")
        email_port = input("输入邮箱服务端口（留空则全局推送信息生效）：")
        while True:
            email_receiver = input("收入接收邮件地址（设置邮件推送时，此项必填）：")
            if "@" not in email_receiver:
                print("\033[31m邮件格式不正确！\033[0m")
                pass
            else:
                break
        userdata = checkUserData(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                                 device=device, modify_coordinates=modify_coordinates, address=address,
                                 pushmode=pushmode,
                                 email_username=email_username, email_password=email_password, email_address=email_address, email_port=email_port, email_receiver=email_receiver)
        pushmode = "邮件推送"
    else:
        userdata = checkUserData(filename=filename, enabled=enabled, day=day, name=name, phone=phone, password=password,
                                 device=device, modify_coordinates=modify_coordinates, address=address,
                                 pushmode=pushmode)
        pushmode = "不推送"
    now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    userForm = f'''姓名：\033[32m{userdata[0][0]['name']}\033[0m\n打卡时间：\033[32m{(datetime.datetime.strptime(userdata[0][0]['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(now_localtime, '%Y-%m-%d %H:%M:%S')).days}\033[0m天\n手机型号：\033[32m{userdata[0][0]['deviceId']}\033[0m\n打卡地址：\033[32m{userdata[0][0]['address']}\033[0m\n推送方式：\033[32m{pushmode}\033[0m\n推送反馈：\033[33m{userdata[1]}\033[0m'''
    print(userForm)
    if "成功" in userdata[2]:
        print("\033[32m写入成功！\033[0m")
    else:
        print(f"\033[31m{userdata[2]}\033[0m")
    input("按任意键退出...")