<h1 align="center">职校家园打卡</h1>

<p align="center"><a href="https://www.gnu.org/licenses/gpl-3.0.zh-cn.html"><img src="https://img.shields.io/badge/licenses-GPL3.0-yellow"></a> <a href="https://www.python.org/"><img src="https://img.shields.io/badge/language-Python-brightgreen"></a> <img src="https://img.shields.io/badge/thank-rialll-red"> <a href="#"><img src="https://visitor-badge.laobi.icu/badge?page_id=zycn0910.Sign-ZXJY"></a></p>

<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=zycn0910/Sign-ZXJY&type=Timeline&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=zycn0910/Sign-ZXJY&type=Timeline" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=zycn0910/Sign-ZXJY&type=Timeline" />
</picture>

## 重要
<font color="red">项目被代挂狗举报，随时删除</font>
> 
> 本项目基于[GPL3.0开源协议](https://www.gnu.org/licenses/gpl-3.0.zh-cn.html)。
> 
> 项目内仅有一处版权信息，详情在`main.py`51行。
> 
> 仅供学习使用，请于下载后24小时内删除项目所有内容。
> 
> 我们不鼓励、不赞成、不支持任何人，使用任何违规方式完成实习和打卡任务。同时，鉴于项目的特殊性，开发者可能在任何时间停止更新或删除项目。
> 
> 您所使用本项目但不仅限于本项目所造成的任何后果均由您本人承担，与项目作者无关，您使用即代表您同意！
> 
> 如基于或参考此项目进行二次开发，请注明原作者并使用GPL3.0许可证。
### 12.9更新日志
1、优化代理ip逻辑，每次运行会获取新的代理ip，本次运行的所有用户均使用此代理，更换代理源为[站大爷](#)
`优：ip质量高` `劣：防火墙严格封禁ip，不宜过度访问`，封禁后解封时间不详，建议每日至多运行两次。

## 介绍
1、增加多种推送模式，例如Pushplus、DingDingWebHook机器人、Server_Turbo推送、自建Smtp邮件推送（邮件推送支持一对多、一对一）。

2、增加打卡倒计时，可设置账号打卡截止时间。

3、增加添加用户功能（可交互和非交互两种）、无需每次更改json文件。

4、优化推送、可设置满足某一条件推送，默认为无论何时运行都推送。详情见config.py第11行。


## 使用说明

平台推荐：7x24小时的Linux系统、Windows系统、青龙面板、云函数、Github Actions等。

### 源码运行

更新
```pip install --upgrade pip```

安装所需依赖
```pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt ```。

添加用户运行
`python AddUser.py`/`python AddUser-noinput.py`。

打卡主程序运行
`python Main.py`。


### Linux系统运行
1、先源码运行一次，然后设置定时任务运行Main.py。

2、[Linux定时任务参考](https://www.runoob.com/w3cnote/linux-crontab-tasks.html).

### 青龙面板

1、面板配置文件20行取消代理，新建定时任务，名称随意，定时随意，运行一次。
```
拉库命令：ql repo https://mirror.ghproxy.com/https://github.com/zycn0910/Sign-ZXJY.git
```


2、在脚本管理zycn0910_Sign-ZXJY文件夹里手动添加`day_report.json`、`week_report.json`、`month_report.json`三个json文件。

2、打开依赖管理，选择python，新建依赖，勾选自动拆分，复制下面的依赖名称。
```
beautifulsoup4==4.12.2
certifi==2023.7.22
charset-normalizer==3.3.0
colorama==0.4.6
docopt==0.6.2
idna==3.4
lxml==4.9.3
requests==2.31.0
soupsieve==2.5
tqdm==4.66.1
urllib3==2.0.7
yarg==0.1.9
```

3、删除拉库命令和拉库时自动添加的多余定时任务，只保留Main，AddUser-noinput两个，暂停AddUser-noinput的定时任务。

4、测试运行Main。

```如果青龙面板python版本小于3.10，在process.py文件29行，删掉encoding="utf-8"参数```

## 推送模块说明

>详情可见项目：[长目飞耳](https://github.com/zycn0910/Message-Push)。

## user.json结构说明

```
{
    # 是否开启打卡
    "enabled": true,
    # 添加日期
    "adddate": "2023-10-15 12:23:32",
    # 打卡结束日期
    "enddate": "2023-10-16 12:23:32",
    # 账号别名
    "name": "测试名字",
    # ZXJY账号
    "phone": "测试账号",
    # ZXJY密码
    "password": "测试密码",
    # 打卡设备型号
    "deviceId": "测试手机型号",
    # 设备token， 添加账号时自动生成
    "dToken": "5xw7cfuznlo13yjv4prt862qiaskhd0meb9g",
    # 随机经纬最后一位数，默认开启
    "modify_coordinates": true,
    # 打卡地址
    "address": "河南郑州",
    # 经度，自动获取
    "longitude": "113.640100",
    # 纬度，自动获取
    "latitude": "34.724680",
    # 推送模式，为空则默认本地控制台
    "pushmode": "",
    # 推送数据
    "pushdata": {
        # DingDing机器人推送，模式1生效
      "Ding": {
        "Secret": null,
        "Token": null
      },
        # Pushplus推送，模式2生效
      "PushPlus": {
        "Token": null
      },
        # Server酱推送，模式3生效
      "Server_Turbo": {
        "Token": null
      },
        # 邮件推送，模式4且config内邮件信息为空生效
      "Email": {
        "Send": null,
        "Password": null,
        "Server_Address": null,
        "Smtp_Port": null,
        "Receiver": null
      }
    }
  }
```
