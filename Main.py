import datetime
import sys
import time
from tqdm import tqdm
import config
import process
import pushinfo


def main(users):
    if config.log_report:
        logData = ""
    else:
        pass
    with tqdm(users, desc=f"用户打卡", total=len(users), unit="人", colour="#00FF00", ncols=100, leave=True,
              position=0,
              file=sys.stdout) as bar:
        for user in bar:
            tqdm.write(f"=========={user['name']}==========")
            waittime = process.random_Time(config.range_time)
            tqdm.write(f"本次随机 {waittime} s")
            # time.sleep(float(waittime))
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(user['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            info = process.login_and_sign_in(user=user, endday=TDOA.days)
            # 处理打卡日志
            try:
                for i in range(0, len(info)):
                    logData = logData + info[i].replace("\n", "").replace("未在", "。  未在").replace("剩余", "。  剩余")
                    i = i + 1
                logData = logData + "\n"
            except:
                pass
            # 打卡日志处理完成
            for i in range(0, len(info)):
                tqdm.write(f"{info[i]}")
                i = i + 1
        bar.close()
        # 发送日志邮件
        if config.log_report:
            email = config.log_report_data
            try:
                print(pushinfo.Send_Email(email['emailUsername'], email['emailPassword'], email['emailAddress'], email['emailPort'], email['Receiver'], "test", logData))
            except Exception as e:
                print(e)
                pass
        else:
            pass


if __name__ == "__main__":
    tqdm.write("项目免费开源，详情见：https://github.com/zycn0910/Sign-ZXJY")
    tqdm.write("\033[32m====================进程开始====================\033[0m")
    main(process.load_users_from_json("all-users.json"))
    tqdm.write("\033[32m====================进程结束====================\033[0m")
