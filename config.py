'''全局推送, 设置后用户单独推送数据将失效'''
pushmode = ""
# 1 钉钉机器人
DingDingSecret = ""
DingDingToken = ""
# 2 PushPlus
PushPlusToken = ""
# 3 Server酱
Server_Turbo = ""
# 4 邮件、用户侧必须配置接收地址
email_username = "@"
email_password = ""
email_address = ""
email_port = ""
'''程序运行时间（满足此时间才推送信息，否则本地输出），早上7点运行时推送，其余时间运行不推送填07，留空为无论何时都推送
'''
time = "07"
'''随机时间'''
# 范围
range_time = (10, 30)
'''腾讯地图api密钥，获取地址经纬度需要'''
# 第三方公开，不保证稳定性
api_token = "UGMBZ-CINWR-DDRW5-W52AK-D3ENK-ZEBRC"

'''是否开启日报、周报、月报（打卡成功才会提交）'''
# 是否开启日报，每日提交
day_report = False
# 是否开启周报，每周日提交
week_report = False
# 是否开启月报，每月30号提交
month_report = False

'''日志，仅支持smtp邮件推送'''
log_report = False
log_report_data = {
    # smtp用户名
    "emailUsername": "",
    # smtp密码
    "emailPassword": "",
    # smtp服务器地址
    "emailAddress": "",
    # smtp端口
    "emailPort": "",
    # 接收日志邮箱
    "Receiver": ""
}
