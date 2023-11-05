import datetime
import os
import random
import sys
import time

from tqdm import tqdm

import config
import process


def sign_main(users):
    with tqdm(users, desc=f"用户打卡", total=len(users), unit="人", colour="#00FF00", ncols=100, leave=True, position=0,
              file=sys.stdout) as bar:
        for user in bar:
            waittime = process.random_Time(config.range_time)
            tqdm.write(f"本次随机 {waittime} s")
            time.sleep(float(waittime))
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(user['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            info = process.login_and_sign_in(user=user, endday=TDOA.days)
            for i in range(0, len(info)):
                tqdm.write(f"{info[i]}")
                i = i + 1
            tqdm.write("====================")
        bar.close()


def report_main(users):
    if config.day_report or config.week_report or config.month_report:
        with tqdm(users, desc=f"提交报告", total=len(users), unit="人", colour="#00FF00", ncols=100, leave=True,
                  position=0,
                  file=sys.stdout) as bar:
            for user in bar:
                waittime = process.random_Time(config.range_time)
                tqdm.write(f"本次随机 {waittime} s")
                time.sleep(float(waittime))
                if config.day_report:
                    day_report_data = process.load_users_from_json("day_report.json")
                    this_day_report_data = day_report_data[random.randint(0, (len(day_report_data) - 1))]
                    this_day_result = process.day_Report(datetime.datetime.now(), user, this_day_report_data['summary'],
                                                         this_day_report_data['recored'],
                                                         this_day_report_data['project'])
                    tqdm.write(
                        f"{user['name']}，日报响应代码：{this_day_result['code']}，响应信息：{this_day_result['msg']}")
                if config.week_report:
                    if datetime.datetime.weekday(datetime.datetime.now()) == 6:
                        week_report_data = process.load_users_from_json("week_report.json")
                        this_week_report_data = week_report_data[random.randint(0, (len(week_report_data) - 1))]
                        this_week_result = process.day_Report(datetime.datetime.now(), user,
                                                              this_week_report_data['summary'],
                                                              this_week_report_data['recored'],
                                                              this_week_report_data['project'])
                        tqdm.write(
                            f"{user['name']}，周报响应代码：{this_week_result['code']}，响应信息：{this_week_result['msg']}")
                if config.month_report:
                    if datetime.datetime.now().strftime("%m") == "30":
                        month_report_data = process.load_report_data_from_json("month_report.json")
                        this_month_report_data = month_report_data[random.randint(0, (len(month_report_data) - 1))]
                        this_month_report_result = process.day_Report(datetime.datetime.now(), user,
                                                                      this_month_report_data['summary'],
                                                                      this_month_report_data['recored'],
                                                                      this_month_report_data['project'])
                        tqdm.write(
                            f"{user['name']}，月报响应代码：{this_month_report_result['code']}，响应信息：{this_month_report_result['msg']}")
                tqdm.write("====================")
            bar.close()
            print("====================报告提交进程已完成====================")
    else:
        print("暂未开启报告提交功能！")


if __name__ == "__main__":
    users_file_path = "all-users.json"
    users = process.load_users_from_json(users_file_path)
    print("项目免费开源，详情见：https://github.com/zycn0910/Sign-ZXJY")
    print("====================开始打卡进程====================")
    sign_main(users)
    print("====================打卡进程已完成====================")
    print("5后开始提交报告进程")
    time.sleep(5)
    try:
        os.system("cls || clear")
    except:
        print("\n" * 100)
    print("====================开始报告提交进程====================")
    report_main(users)
