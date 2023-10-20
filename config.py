'''全局推送, 设置后用户单独推送数据将失效'''
import random

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
'''程序运行时间（满足此时间才推送信息，否则本地输出）
早上7点运行时推送，其余时间运行不推送填07
留空为无论何时都推送
'''
time = ""
'''随机时间范围10——30秒'''
range_time = random.randint(10, 30)
'''腾讯地图api密钥，获取地址经纬度需要'''
# 第三方公开，不保证稳定性
api_token = "UGMBZ-CINWR-DDRW5-W52AK-D3ENK-ZEBRC"

