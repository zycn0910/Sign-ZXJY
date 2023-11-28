import base64
import smtplib
import urllib

from email.mime.text import MIMEText
from process import *


def DingTalkRebot(DingSecret, DingToken, title, content):
    timestamp = str(round(time.time() * 1000))
    secret = DingSecret
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    rebot_address = "https://oapi.dingtalk.com/robot/send?access_token="
    ding_token = DingToken
    head = {"content-type": "application/json"}
    message = {"msgtype": "text", "text": {"content": title + f"\n{content}"}}
    post = requests.post(rebot_address + ding_token + "&timestamp=" + timestamp + "&sign=" + sign, json=message,
                         headers=head)
    if post.json()["errcode"] == 0:
        return "成功推送至DingDing！"
    else:
        errcode = post.json()["errcode"]
        errmsg = post.json()["errmsg"]
        return f"推送失败！\n响应代码：{errcode}\n{errmsg}"


def PushPlus(token, title, content):
    url = 'http://www.pushplus.plus/send'
    data = {"token": token, "title": title, "content": content}
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    post = requests.post(url, data=body, headers=headers)
    if post.json()["code"] == 200:
        return "成功推送至PushPlus！"
    else:
        errcode = post.json()["code"]
        errmsg = post.json()["msg"]
        return f"推送失败！\n响应代码：{errcode}\n错误描述：{errmsg}"


def ServerTurbo(token, title, content):
    url = "https://sctapi.ftqq.com/"
    head = {"Content-type": "application/json"}
    get = requests.post(url + "/" + token + ".send?title=" + title + "&desp=" + content, headers=head)
    if get.json()["code"] == 0:
        return "成功推送至Server酱！"
    else:
        errcode = get.json()["code"]
        errmsg = get.json()["message"]
        return f"推送失败！\n响应代码：{errcode}\n错误描述：{errmsg}"


def Send_Email(Send, Password, Server_Address, Smtp_Port, Receiver, title, content):
    if Send is None or Send == '@':
        return f"{Send}，邮箱格式不正确"
    try:
        smtp = smtplib.SMTP_SSL(host=Server_Address, port=Smtp_Port)
        smtp.connect(host=Server_Address, port=Smtp_Port)
        smtp.login(user=Send, password=Password)
        message = MIMEText(content, 'plain', 'utf-8')
        message['Subject'] = title
        message['From'] = Send
        message['To'] = Receiver
        smtp.sendmail(from_addr=Send, to_addrs=Receiver, msg=message.as_string())
        smtp.quit()
        return f"成功发送邮件到：{Receiver}"
    except Exception as e:
        return f"邮件发送失败！错误描述：{e}"
