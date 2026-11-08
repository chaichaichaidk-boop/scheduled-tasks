# encoding:utf-8
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

PUSHPLUS_API = "http://www.pushplus.plus/send"
BEIJING_TZ = timezone(timedelta(hours=8))


def send_notification(token, title, content, template="markdown"):
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": template,
    }
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8")
    response = requests.post(PUSHPLUS_API, data=body, headers=headers, timeout=30)
    result = response.json()
    if result.get("code") == 200:
        print(f"推送成功: {title}")
    else:
        print(f"推送失败: {result.get('msg')}")
    return result


def log(logs, msg):
    print(msg)
    logs.append(msg)


def get_user_info(token, logs):
    headers = {
        "Host": "gw2c-hw-open.longfor.com",
        "Connection": "keep-alive",
        "X-LF-Api-Version": "v2_6_0",
        "X-Gaia-Api-Key": "98717e7a-a039-46af-8143-be7558a089c0",
        "X-LF-Bucode": "C20400",
        "content-type": "application/json",
        "X-LF-Channel": "C2",
        "lmToken": token,
        "Accept-Encoding": "gzip,compress,br,deflate",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.80(0x18005030) NetType/WIFI Language/zh_CN",
        "Referer": "https://servicewechat.com/wx50282644351869da/525/page-frame.html"
    }
    url = 'https://gw2c-hw-open.longfor.com/supera/member/api/bff/pages/v2_6_0/v1/user-info'
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        log(logs, f"获取用户信息异常: {e}")
        return

    if response.status_code == 200:
        try:
            resp_json = response.json()
            code = resp_json.get("code")
            message = resp_json.get("message", "")
            data = resp_json.get("data", {})
            if code == "0000":
                level_name = data.get("levelName", 0)
                growth_value = data.get("growthValue", 0)
                next_level_growth_value = data.get("nextLevelGrowthValue", 0)
                log(logs, f"当前等级: {level_name}, 当前成长值: {growth_value}, 下一级成长值: {next_level_growth_value}")
            elif code == "801001":
                log(logs, f"获取用户信息失败：{message}")
            else:
                log(logs, f"获取用户信息失败，错误代码: {code}, 错误信息: {message}")
        except json.JSONDecodeError:
            log(logs, f"获取用户信息失败，响应解析错误: {response.text}")
    else:
        log(logs, f"获取用户信息失败，状态码: {response.status_code}, 错误信息: {response.text}")


def checkin(token, logs):
    headers = {
        "Host": "gw2c-hw-open.longfor.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.80(0x18005030) NetType/WIFI Language/zh_CN miniProgram/wx50282644351869da",
        "Referer": "https://longzhu.longfor.com/",
        "X-GAIA-API-KEY": "c06753f1-3e68-437d-b592-b94656ea5517",
        "X-LF-DXRisk-Captcha-Token": "undefined",
        "Origin": "https://longzhu.longfor.com",
        "X-LF-UserToken": token,
        "X-LF-DXRisk-Source": "5",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Site": "same-site",
        "X-LF-Channel": "C2",
        "X-LF-DXRisk-Token": "6aefe56dRbsFALbLfiZJEzUAPxPPsbZfGTy1LXj1",
        "Content-Length": "50",
        "Connection": "keep-alive",
        "token": token,
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "X-LF-Bu-Code": "C20400",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Mode": "cors"
    }
    cookies = {
        "acw_tc": "276077a917941068459883448e6ba9bb6a38c53f9ef341cb2067c1770f37c8"
    }
    url = 'https://gw2c-hw-open.longfor.com/lmarketing-task-api-mvc-prod/openapi/task/v1/signature/clock'
    data = {
        "activity_no": "11111111111686241863606037740000"
    }
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data, timeout=15)
    except Exception as e:
        log(logs, f"签到请求异常: {e}")
        return

    if response.status_code == 200:
        try:
            resp_json = response.json()
            code = resp_json.get("code")
            message = resp_json.get("message", "")
            data = resp_json.get("data", {})

            if code == "0000":
                is_popup = data.get("is_popup", 0)
                if is_popup == 1:
                    reward_info = data.get("reward_info", [])
                    if reward_info:
                        reward_num = reward_info[0].get("reward_num", 0)
                        log(logs, f"龙湖天街签到成功！获得了 {reward_num} 个成长值")
                    else:
                        log(logs, "龙湖天街签到成功！")
                else:
                    log(logs, "龙湖天街今天已经签过到了")
            elif code == "801001":
                log(logs, f"龙湖天街签到失败：{message}")
            else:
                log(logs, f"龙湖天街签到失败，错误代码: {code}, 错误信息: {message}")
        except json.JSONDecodeError:
            log(logs, f"龙湖天街签到失败，响应解析错误: {response.text}")
    else:
        log(logs, f"龙湖天街签到失败，状态码: {response.status_code}, 错误信息: {response.text}")


def main():
    pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
    if not pushplus_token:
        print("错误: 未设置 PUSHPLUS_TOKEN")
        sys.exit(1)

    # 天街 lmToken 也建议放环境变量，避免硬编码
    lf_token = os.environ.get("LF_TOKEN", "")

    now = datetime.now(BEIJING_TZ)
    title = f"天街签到通知 - {now.strftime('%m月%d日')}"

    logs = []
    get_user_info(lf_token, logs)
    checkin(lf_token, logs)

    # 用 markdown 模板拼推送正文
    content = f"""## 天街签到报告

**时间**: {now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)

---

{chr(10).join('- ' + line for line in logs)}

---

> 此消息由定时任务自动发送
"""

    send_notification(pushplus_token, title, content)


if __name__ == "__main__":
    main()
