import datetime
import logging
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
            logging.info(f"{user['name']} 随机 {waittime} s")
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(user['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            info = process.login_and_sign_in(user=user, endday=TDOA.days)
            logging.info(f"{user['name']} 的返回值为{info}")
            if config.log_report:
                try:
                    for i in range(0, len(info)):
                        logData = logData + info[i].replace("\n", "").replace("未在", "。未在").replace("剩余", "。剩余")
                    logData = logData + "\n"
                except:
                    pass
            else:
                pass
            for i in range(0, len(info)):
                tqdm.write(f"{info[i]}")
        if config.log_report:
            logging.info(
                pushinfo.Send_Email(config.log_report_data['emailUsername'], config.log_report_data['emailPassword'],
                                    config.log_report_data['emailAddress'],
                                    config.log_report_data['emailPort'], config.log_report_data['Receiver'], "test",
                                    logData))
    bar.close()


if __name__ == "__main__":
    tqdm.write("项目免费开源，详情见：https://github.com/zycn0910/Sign-ZXJY")
    tqdm.write("\033[32m====================进程开始====================\033[0m")
    main(process.load_users_from_json("all-users.json"))
    tqdm.write("\033[32m====================进程结束====================\033[0m")
