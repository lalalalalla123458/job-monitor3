import requests
from bs4 import BeautifulSoup
import smtplib
import ssl
from email.mime.text import MIMEText
import os
from datetime import datetime

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# 你可报考的核心关键词
MATCH_KEYWORDS = [
    "生物", "生命科学", "医学", "医药", "药学",
    "食品", "农学", "医疗器械",
    "市场监督", "药品监管",
    "科技管理", "技术岗", "管理岗"
]

# 监控地区
URLS = {
    "广东人社": "http://hrss.gd.gov.cn/gkmlpt/index",
    "湖南人社": "http://rst.hunan.gov.cn/rst/xxgk/zpzl/",
    "重庆人社": "http://rlsbj.cq.gov.cn/zwxx_182/sydw/",
    "浙江人社": "http://rlsbt.zj.gov.cn/col/col1229743683/index.html",
    "上海人社": "https://rsj.sh.gov.cn/trsrc_177/"
}


def send_email(content):
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "事业单位岗位监控结果"

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())


def fetch_jobs():
    results = []

    for region, url in URLS.items():
        try:
            response = requests.get(url, timeout=15)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "lxml")

            for link in soup.find_all("a"):
                title = link.get_text().strip()

                if "招聘" not in title and "事业单位" not in title:
                    continue

                job_url = link.get("href")
                if not job_url:
                    continue

                if not job_url.startswith("http"):
                    job_url = url.rstrip("/") + "/" + job_url.lstrip("/")

                try:
                    detail = requests.get(job_url, timeout=15)
                    detail.encoding = "utf-8"
                    text = detail.text

                    if any(word in text for word in MATCH_KEYWORDS):
                        results.append(f"{region} | {title}\n{job_url}\n")

                except:
                    continue

        except:
            continue

    return results


if __name__ == "__main__":
    jobs = fetch_jobs()

    today = datetime.now().strftime("%Y-%m-%d")

    if jobs:
        content = f"{today} 匹配到以下岗位：\n\n" + "\n".join(jobs)
    else:
        content = f"{today} 今日未发现匹配岗位。"

    send_email(content)
