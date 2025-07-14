import time, os, sys
import pickle
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import tempfile

def human_scroll(driver, steps=5):
    for i in range(steps):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(random.uniform(1, 2))


# === STEP 1: Setup với cookies ===
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

# Tạo temp folder riêng cho mỗi process
tmp_dir = tempfile.mkdtemp(prefix="uc_temp_")
driver = uc.Chrome(options=options, 
                   user_data_dir=tmp_dir,
                   driver_executable_path="uc/undetected_chromedriver_1.exe")
driver.set_window_position(0, 0)   # top-left
driver.set_window_size(500, 400)

try: 
    driver.get("https://www.tiktok.com/")

    # === STEP 2: Load cookies ===
    cookies = pickle.load(open("cookies/tiktok_cookies.pkl", "rb"))
    for cookie in cookies:
        if "sameSite" in cookie:
            cookie.pop("sameSite")
        driver.add_cookie(cookie)

    driver.get("https://www.tiktok.com/@raumamix.official")
    time.sleep(2)

    # === STEP 3: Lấy followers & likes ===
    followers = driver.find_element(By.CSS_SELECTOR, '[data-e2e="followers-count"]').text
    likes = driver.find_element(By.CSS_SELECTOR, '[data-e2e="likes-count"]').text

    print(f"Followers: {followers}, Likes: {likes}")

    # === STEP 4: Scroll để load video ===
    human_scroll(driver, steps=5)
    time.sleep(2)

    # === STEP 5: Tìm các link video ===
    video_links = []
    video_items = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a')
    for item in video_items:
        href = item.get_attribute('href')
        if href:
            video_links.append(href)

    print(f"Tìm thấy {len(video_links)} video")

    # === STEP 6: Crawl từng video ===
    videos_data = []

    for link in video_links[:10]:
        driver.get(link)
        time.sleep(random.uniform(1, 3))

        like = driver.find_element(By.CSS_SELECTOR, '[data-e2e="like-count"]').text
        comment = driver.find_element(By.CSS_SELECTOR, '[data-e2e="comment-count"]').text
        share = driver.find_element(By.CSS_SELECTOR, '[data-e2e="share-count"]').text

        videos_data.append({
            "url": link,
            "likes": like,
            "comments": comment,
            "shares": share
        })

        print(f"Video: {link} | Likes: {like} | Comments: {comment} | Shares: {share}")


    # Ghi ra file
    with open("data/tiktok.txt", "w", encoding="utf-8") as f:
        f.write(f"Followers: {followers}\n")
        f.write(f"Likes: {likes}\n\n")
        f.write("=== 10 Recent Videos ===\n")
        for v in videos_data:
            f.write(f"{v}\n")

finally:
    driver.quit()
    sys.exit(0)
