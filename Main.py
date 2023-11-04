import datetime
import sys
import time

from tqdm import tqdm

import config
import process

if __name__ == "__main__":
    print("项目免费开源，详情见：https://github.com/zycn0910/Sign-ZXJY")
    users_file_path = "all-users.json"
    users = process.load_users_from_json(users_file_path)
    with tqdm(users, desc=f"打卡", total=len(users), unit="人", colour="#00FF00", ncols=100, leave=True, position=0,
              file=sys.stdout) as bar:
        for user in bar:
            waittime = config.range_time
            tqdm.write(f"本次随机 {waittime} s")
            # time.sleep(float(waittime))
            now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            TDOA = datetime.datetime.strptime(user['enddate'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(
                now_localtime, '%Y-%m-%d %H:%M:%S')
            info = process.login_and_sign_in(user=user, endday=TDOA.days)
            for i in range(0, len(info)):
                tqdm.write(f"{info[i]}")
                i = i + 1
            tqdm.write("====================")
        bar.close()
