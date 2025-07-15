from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pickle
import time
import random
import re, os, sys
import tempfile
import argparse

def human_scroll(driver, steps=10):
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(random.uniform(1, 2))


def parse_number(text):
    multipliers = {"K": 1_000, "M": 1_000_000}
    text = text.replace(',', '').strip()
    if not text:
        return 0
    try:
        if text[-1] in multipliers:
            return int(float(text[:-1]) * multipliers[text[-1]])
        return int(text)
    except:
        return 0


def get_likes_followers(driver):
    likes, followers = "?", "?"
    try:
        likes_elem = driver.find_element(By.XPATH, '//a[contains(@href,"friends_likes")]//strong')
        likes = likes_elem.text
    except:
        pass
    try:
        followers_elem = driver.find_element(By.XPATH, '//a[contains(@href,"followers")]//strong')
        followers = followers_elem.text
    except:
        pass
    return likes, followers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--link')
    args = parser.parse_args()

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")

    # Tạo temp folder riêng cho mỗi process
    tmp_dir = tempfile.mkdtemp(prefix="uc_temp_")
    driver = uc.Chrome(options=options, 
                       user_data_dir=tmp_dir,
                       driver_executable_path="uc/undetected_chromedriver_2.exe")
    driver.set_window_position(1000, 0)   # top-left
    driver.set_window_size(500, 400)

    driver.get("https://www.facebook.com/")
    cookies = pickle.load(open("cookies/fb_cookies.pkl", "rb"))
    for cookie in cookies:
        if 'sameSite' in cookie:
            cookie.pop('sameSite')
        driver.add_cookie(cookie)

    driver.get(args.link)
    time.sleep(5)

    likes, followers = get_likes_followers(driver)
    print(f"Page Likes: {likes}, Followers: {followers}")

    human_scroll(driver, steps=5)
    time.sleep(3)

    reaction_spans = driver.find_elements(By.XPATH, '//span[@aria-label="See who reacted to this"]')
    print(f"Found {len(reaction_spans)} reaction spans")
    
    post_data = []

    for idx, span in enumerate(reaction_spans):
        if idx >= 10:
            break

        driver.execute_script("arguments[0].scrollIntoView(true);", span)
        time.sleep(0.5)

        parent = span.find_element(By.XPATH, '..')
        next_div = parent.find_element(By.XPATH, 'following-sibling::div[1]')
        next_text = next_div.text

        # Tách số comment/share từ sibling div
        comment_num, share_num = 0, 0
        lines = next_text.lower().split('\n')

        for line in lines:
            if 'comment' in line:
                nums = re.findall(r'[\d,.KM]+', line)
                if nums:
                    comment_num = parse_number(nums[0])
            elif 'share' in line:
                nums = re.findall(r'[\d,.KM]+', line)
                if nums:
                    share_num = parse_number(nums[0])

        # Tìm reactions gần nhất
        try:
            reactions_div = parent.find_element(
                By.XPATH,
                './/div[contains(text(),"All reactions:")]'
            )
            reactions_span = reactions_div.find_element(
                By.XPATH,
                './following-sibling::span[1]'
            )
            reaction_num = parse_number(reactions_span.text)
        except:
            reaction_num = 0

        res = {
            "num_reaction": reaction_num,
            "num_comment": comment_num,
            "num_share": share_num
        }

        print(f"\n=== POST {idx+1} ===")
        print(res)

        post_data.append(res)

    # Ghi ra file
    with open("data/fb.txt", "w", encoding="utf-8") as f:
        f.write(f"Followers: {followers}\n")
        f.write(f"Likes: {likes}\n\n")
        f.write("=== 10 Recent Post ===\n")
        for p in post_data:
            f.write(f"{p}\n")

    driver.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
