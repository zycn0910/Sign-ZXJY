<h1 align="center">职校家园打卡</h1>

<p align="center"><a href="https://www.gnu.org/licenses/gpl-3.0.zh-cn.html"><img src="https://img.shields.io/badge/licenses-GPL3.0-yellow"></a> <a href="https://www.python.org/"><img src="https://img.shields.io/badge/language-Python-brightgreen"></a> <img src="https://img.shields.io/badge/thank-rialll-red"> <a href="#"><img src="https://visitor-badge.laobi.icu/badge?page_id=zycn0910.Sign-ZXJY"></a></p>

<hr>
<hr>

### 2024.9.1更新日志
1、重构openai生成实习报告模块。
2、添加配置文件详解。

### 2024.5.16更新日志
1、节假日判断取[国务院调休数据](https://www.gov.cn/zhengce/content/202310/content_6911527.htm)。

### 2024.2.19更新日志
1、增加节假日判断，如果当天为中国法定节假日，则跳过打卡和提交实习报告。默认为关，见config.yml第43-44行。

### 2023.12.9更新日志
1、优化代理ip逻辑，每次运行会获取新的代理ip，本次运行的所有用户均使用此代理，更换代理源为[站大爷]()
`优：ip质量高` `劣：防火墙严格封禁ip，不宜过度访问`，封禁后解封时间不详，建议每日至多运行两次。

### 2023.12.31更新日志
1、实习报告提交接入ChatGPT，使用GPT官方库，可使用任何支持官方接口的国内镜像站，所提交的数据经过GPT三次处理，以求达到精准。如需自定义提示词，移步`process.py`第390行`prompt_handler`函数
```
config.yml第31行配置说明：
url：请求地址
# 例如chateverywhere的地址为：api.chatanywhere.com.cn，需填写https://api.chatanywhere.com.cn/v1
key：秘钥
# 填写sk-xxxxxx，注意‘sk-’不要省略
```
建议使用chateverywhere免费接口（有限制），如使用付费接口，推荐[GPT官方](https://chat.openai.com/)、[API2D](https://api2d.com/r/218099)、[OhMyGPT](https://aigptx.top?aff=I3K0Ufov)，链接中可能带了邀请码，如果您不需要，可以删掉某些选项，直接访问官网。

### 2023.11.15更新日志
1、增加代理设置，代理数据来自[快代理/免费代理](https://www.kuaidaili.com)，见`config.py`34行。

    代理说明：每次运行爬取一条可用代理数据，然后本次运行内的所有网络请求均用此代理。

### 2023.11.11更新日志
1、修复实习报告提交bug。

### 2023.11.5更新日志
1、修复打卡地址变成手机号。

2、添加实习报告提交功能（默认关闭，`config.py`里开启），开启前请修改`day_report.json`、`week_report.json`、`month_report.json`内的数据内容。开启后每次提交对应文件内的随机一条数据。

### 2023.11.4更新日志
1、使用[rialll](https://github.com/fuckZXJY)算法。

### 2023.11.1更新日志
1、APP更新验证版本，本脚本同步更新。

### 2023.10.20更新（可能防作弊）日志
1、自动判断手机操作系统，添加用户时，手机型号设置为iPhone系列或者Android系列，使用不同的请求头。

2、自动获取版本号，Android最新版本号为57(程序内写死)、iOS自动获取App Store最新版本号。

3、随机用户打卡时间。
