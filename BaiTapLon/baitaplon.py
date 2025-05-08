import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import schedule
import time

def crawl_vnexpress():
    url = "https://vnexpress.net/suc-khoe"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article")
    data = []

    for article in articles:
        try:
            title_tag = article.find("h3", class_="title-news")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.find("a")["href"]
            img_tag = article.find("img")
            image = img_tag["data-src"] if img_tag and "data-src" in img_tag.attrs else ""

            article_page = requests.get(link)
            article_soup = BeautifulSoup(article_page.content, "html.parser")
            description_tag = article_soup.find("p", class_="description")
            description = description_tag.get_text(strip=True) if description_tag else ""
            content_div = article_soup.find("article", class_="fck_detail")
            content = "\n".join([p.get_text(strip=True) for p in content_div.find_all("p")]) if content_div else ""

            data.append({
                "Tiêu đề": title,
                "Mô tả": description,
                "Hình ảnh": image,
                "Nội dung": content,
            })
        except Exception as e:
            print(f"Lỗi ở bài viết: {e}")
            continue

    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"vnexpress{today}.xlsx"
    
    try:
        df = pd.DataFrame(data, columns=["Tiêu đề", "Mô tả", "Hình ảnh", "Nội dung"])
        df.to_excel(filename, index=False)
        print(f"Đã lưu file thành công: {os.path.abspath(filename)}")
    except PermissionError:
        print(f"Không thể ghi vào tệp {filename}, hãy đóng tệp Excel nếu đang mở.")
    
def job():
    crawl_vnexpress()

schedule.every().day.at("22:25").do(job)

print("Cho chạy lúc 6h sáng mỗi ngày...")

while True:
    schedule.run_pending()
    time.sleep(60)
