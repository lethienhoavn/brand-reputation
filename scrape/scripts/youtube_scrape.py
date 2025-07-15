import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re, os, sys, argparse
import tempfile


def human_scroll(driver, steps=3):
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(1)


def parse_number(text):
    multipliers = {"K": 1_000, "M": 1_000_000}
    text = text.replace(',', '').replace('.', '').strip()
    try:
        if text[-1] in multipliers:
            return int(float(text[:-1]) * multipliers[text[-1]])
        return int(text)
    except:
        return text


def get_channel_stats(driver, channel_url):
    driver.get(channel_url + "/about")
    time.sleep(1)

    subscribers = videos = views = "?"

    # Xác định div cha
    about_div = driver.find_element(By.XPATH, '//div[@id="additional-info-container"]')
    rows = about_div.find_elements(By.XPATH, './/tr')

    for row in rows:
        text = row.find_element(By.XPATH, './/td[2]').text.strip().lower()

        if "subscribers" in text:
            subscribers = text
        elif "videos" in text:
            videos = text
        elif "views" in text:
            views = text

    return subscribers, videos, views



def get_recent_videos(driver, channel_url):
    # 1️⃣ Vào trang videos
    driver.get(channel_url + "/videos")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="contents"]'))
    )
    human_scroll(driver, steps=2)

    # 2️⃣ Lấy sẵn danh sách hrefs
    video_links = driver.find_elements(By.XPATH, '//div[@id="contents"]//a[@id="thumbnail"]')
    hrefs = []
    for video in video_links:
        href = video.get_attribute("href")
        if href and "watch" in href:
            hrefs.append(href)
        if len(hrefs) >= 10:
            break
    # Loại duplicate nhưng giữ thứ tự
    hrefs = list(dict.fromkeys(hrefs))
    hrefs = hrefs[:5]        

    videos_data = []

    # 3️⃣ Vòng lặp chạy trên list hrefs
    for idx, href in enumerate(hrefs):
        print(f"\n=== Video {idx + 1} ===")
        print("URL:", href)

        driver.get(href)
        time.sleep(1)

        ## ===== Lấy số views =====
        views_text = "?"
        try:
            info_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "info-container"))
            )
            spans = info_div.find_elements(By.TAG_NAME, "span")
            for span in spans:
                txt = span.text.strip()
                if "view" in txt.lower():
                    views_text = txt
                    break
        except:
            pass

        ## ===== Lấy số likes =====
        likes_text = "?"
        try:
            like_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "like-button-view-model"))
            )
            divs = like_button.find_elements(By.XPATH, ".//div")
            for div in divs:
                txt = div.text.strip()
                if txt and txt[0].isdigit():
                    likes_text = txt
                    break
        except:
            pass

        ## ===== Lấy số comments =====

        # Bước 1: Scroll dần nhiều bước để lazy load phần comments
        scroll_pause_time = 1
        scroll_step = 1500

        for _ in range(5):  # tùy page dài ngắn
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(scroll_pause_time)

        # Bước 2: Tìm thẻ comments và scroll thẳng tới nó
        comments_text = "?"
        try:
            ytd_comments = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//ytd-comments[@id="comments"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", ytd_comments)
            time.sleep(1)  # chờ lazy load

            # Lấy leading-section
            leading = ytd_comments.find_element(By.ID, "leading-section")

            spans = leading.find_elements(By.TAG_NAME, "span")
            for i, span in enumerate(spans):
                if "Comments" in span.text:
                    if i > 0:
                        comments_text = spans[i - 1].text.strip()
                    break

        except Exception as e:
            print("❌ Không tìm thấy comments:", e)


        print(f"Views: {views_text}")
        print(f"Likes: {likes_text}")
        print(f"Comments: {comments_text}")

        videos_data.append({
            "url": href,
            "views": views_text,
            "likes": likes_text,
            "comments": comments_text
        })

    return videos_data



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--link')
    args = parser.parse_args()

    channel_url = args.link

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    # Tạo temp folder riêng cho mỗi process
    tmp_dir = tempfile.mkdtemp(prefix="uc_temp_")
    driver = uc.Chrome(options=options, 
                       user_data_dir=tmp_dir,
                       driver_executable_path="uc/undetected_chromedriver_3.exe")
    driver.set_window_position(500, 0)   # top-left
    driver.set_window_size(500, 400)

    try:
        subs, num_videos, total_views = get_channel_stats(driver, channel_url)
        print(f"\nSubscribers: {subs}")
        print(f"Total Videos: {num_videos}")
        print(f"Total Views: {total_views}")

        videos = get_recent_videos(driver, channel_url)

        # Ghi ra files
        with open("data/youtube.txt", "w", encoding="utf-8") as f:
            f.write(f"Subscribers: {subs}\n")
            f.write(f"Total Videos: {num_videos}\n")
            f.write(f"Total Views: {total_views}\n\n")
            f.write("=== 5 Recent Videos ===\n")
            for v in videos:
                f.write(f"{v}\n")

    finally:
        driver.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
